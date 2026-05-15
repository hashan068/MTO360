"""Quality seed: inspection points, results, defects, NCRs, CAPAs, holds, rework."""
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.manufacturing import (
    ManufacturingOrderOperation,
    OperationStatusEnum,
)
from app.models.quality import (
    ActionTypeEnum,
    CAPAStatusEnum,
    CorrectiveAction,
    Defect,
    DefectStatusEnum,
    DefectTypeEnum,
    DispositionEnum,
    HoldStatusEnum,
    HoldTypeEnum,
    InspectionPoint,
    InspectionResult,
    InspectionResultEnum,
    InspectionTypeEnum,
    NCRStatusEnum,
    NonConformanceReport,
    PriorityEnum,
    QualityHold,
    ResponsiblePartyEnum,
    SeverityEnum,
)

from scripts.seed._session import fake, random
from scripts.seed._timeline import NOW, TODAY, days_ago


DEFECT_CATEGORIES = {
    DefectTypeEnum.WORKMANSHIP: ["Cold solder joint", "Wrong component orientation", "Missing component", "Insulation tear"],
    DefectTypeEnum.MATERIAL: ["Out-of-spec capacitor", "Damaged enclosure", "Faulty toroid", "Lifted PCB pad"],
    DefectTypeEnum.DESIGN: ["Thermal hotspot", "Insufficient creepage", "EMC margin"],
    DefectTypeEnum.OTHER: ["ESD damage in handling", "Transport scuff"],
}


async def seed(session: AsyncSession, refs: dict) -> dict:
    users = refs["users"]
    routes = refs["routes"]
    route_ops_by_family = refs["route_ops_by_family"]
    components = refs["components"]
    manufacturing_orders = refs["manufacturing_orders"]
    blocked_mo = refs.get("blocked_mo")

    inspector_users = [users["qa_eng_1"], users["qa_eng_2"]]
    suppliers = refs["suppliers"]

    # Inspection Points: 1-2 per route operation + 1 final per route
    inspection_points: list[InspectionPoint] = []
    final_points_by_family: dict[str, InspectionPoint] = {}
    for family_key, route_ops in route_ops_by_family.items():
        for ro in route_ops:
            ip = InspectionPoint(
                route_operation_id=ro.id,
                inspection_type=InspectionTypeEnum.IN_PROCESS,
                name=f"In-Process Check — {ro.name}",
                description=f"Standard in-process checks for {ro.name}",
                is_required=True,
                checklist_items=[
                    {"item": "Visual conformance", "pass_criteria": "No visible defects"},
                    {"item": "Dimensional", "pass_criteria": "Within drawing tolerance"},
                ],
            )
            session.add(ip)
            inspection_points.append(ip)
        # final
        anchor_ro = route_ops[-1]
        fp = InspectionPoint(
            route_operation_id=anchor_ro.id,
            inspection_type=InspectionTypeEnum.FINAL,
            name=f"Final Inspection — {routes[family_key].name}",
            description="End-of-line acceptance test (functional, hi-pot, label/packaging).",
            is_required=True,
            checklist_items=[
                {"item": "Output voltage", "pass_criteria": "230 ±2% Vrms"},
                {"item": "Output frequency", "pass_criteria": "50 ±0.5 Hz"},
                {"item": "Hi-pot", "pass_criteria": "No breakdown @ 1.5kV"},
                {"item": "Label & serial", "pass_criteria": "Matches batch record"},
            ],
        )
        session.add(fp)
        inspection_points.append(fp)
        final_points_by_family[family_key] = fp
    await session.flush()

    # InspectionPoint lookup by route_operation_id (in-process)
    ip_by_route_op_id: dict[int, InspectionPoint] = {ip.route_operation_id: ip for ip in inspection_points if ip.inspection_type == InspectionTypeEnum.IN_PROCESS}

    # Sample completed/in-progress MO operations for inspections
    completed_ops_q = await session.execute(
        select(ManufacturingOrderOperation).where(
            ManufacturingOrderOperation.status.in_([OperationStatusEnum.COMPLETED, OperationStatusEnum.IN_PROGRESS, OperationStatusEnum.BLOCKED])
        )
    )
    completed_ops = list(completed_ops_q.scalars())
    random.shuffle(completed_ops)
    sample_ops = completed_ops[:120]

    inspection_results: list[InspectionResult] = []
    fail_results: list[InspectionResult] = []
    for op in sample_ops:
        if op.route_operation_id is None or op.route_operation_id not in ip_by_route_op_id:
            continue
        ip = ip_by_route_op_id[op.route_operation_id]
        # 85% pass, 12% fail, 3% conditional
        roll = random.random()
        if roll < 0.85:
            result = InspectionResultEnum.PASS
        elif roll < 0.97:
            result = InspectionResultEnum.FAIL
        else:
            result = InspectionResultEnum.CONDITIONAL
        ir = InspectionResult(
            inspection_point_id=ip.id,
            mo_operation_id=op.id,
            manufacturing_order_id=op.manufacturing_order_id,
            inspector_id=random.choice(inspector_users).id,
            inspection_date=(op.actual_end or op.scheduled_end or NOW),
            result=result,
            checklist_results=[
                {"item": "Visual conformance", "result": result.value, "notes": "" if result == InspectionResultEnum.PASS else "deviation noted"},
                {"item": "Dimensional", "result": "pass" if result != InspectionResultEnum.FAIL else "fail", "notes": ""},
            ],
            notes=fake.sentence(nb_words=8),
        )
        session.add(ir)
        inspection_results.append(ir)
        if result == InspectionResultEnum.FAIL:
            fail_results.append(ir)
    await session.flush()

    # Defects: 13 total — 8 open, 5 closed; 1 critical → quality hold
    defects: list[Defect] = []
    critical_defect: Defect | None = None
    used_results = list(fail_results)
    random.shuffle(used_results)

    open_count, closed_count = 8, 5
    plan: list[tuple[DefectStatusEnum, SeverityEnum]] = []
    plan.append((DefectStatusEnum.OPEN, SeverityEnum.CRITICAL))
    plan.append((DefectStatusEnum.INVESTIGATING, SeverityEnum.MAJOR))
    plan.extend([(DefectStatusEnum.OPEN, SeverityEnum.MAJOR)] * 3)
    plan.extend([(DefectStatusEnum.OPEN, SeverityEnum.MINOR)] * 3)
    plan.extend([(DefectStatusEnum.CLOSED, SeverityEnum.MINOR)] * 3)
    plan.extend([(DefectStatusEnum.RESOLVED, SeverityEnum.MAJOR)] * 2)

    for i, (status, severity) in enumerate(plan):
        ir = used_results[i] if i < len(used_results) else None
        dtype = random.choice(list(DEFECT_CATEGORIES.keys()))
        responsibility = ResponsiblePartyEnum.INTERNAL if dtype != DefectTypeEnum.MATERIAL else ResponsiblePartyEnum.SUPPLIER
        defect = Defect(
            defect_number=f"DEF-{TODAY.strftime('%Y%m%d')}-{i+1:04d}",
            manufacturing_order_id=ir.manufacturing_order_id if ir else (blocked_mo.id if blocked_mo else manufacturing_orders[0].id),
            mo_operation_id=ir.mo_operation_id if ir else None,
            inspection_result_id=ir.id if ir else None,
            defect_type=dtype,
            defect_category=random.choice(DEFECT_CATEGORIES[dtype]),
            severity=severity,
            description=fake.paragraph(nb_sentences=2),
            location=random.choice(["Main board U7 area", "Toroid lead-out", "Heat-sink interface", "AC terminal block", "Display ribbon"]),
            quantity_affected=random.randint(1, 4),
            root_cause=fake.sentence(nb_words=12) if status in (DefectStatusEnum.INVESTIGATING, DefectStatusEnum.RESOLVED, DefectStatusEnum.CLOSED) else None,
            reported_by_id=random.choice(inspector_users).id,
            responsible_party=responsibility,
            supplier_id=random.choice(suppliers).id if responsibility == ResponsiblePartyEnum.SUPPLIER else None,
            status=status,
        )
        session.add(defect)
        defects.append(defect)
        if severity == SeverityEnum.CRITICAL and critical_defect is None:
            critical_defect = defect
    await session.flush()

    # Tie the critical defect to the blocked MO if available
    if blocked_mo and critical_defect:
        critical_defect.manufacturing_order_id = blocked_mo.id

    # NCRs: 3 total — 1 open, 1 pending_approval, 1 closed
    ncrs: list[NonConformanceReport] = []
    ncr_plans = [
        (NCRStatusEnum.OPEN, PriorityEnum.URGENT, critical_defect),
        (NCRStatusEnum.PENDING_APPROVAL, PriorityEnum.HIGH, defects[1] if len(defects) > 1 else None),
        (NCRStatusEnum.CLOSED, PriorityEnum.NORMAL, next((d for d in defects if d.status == DefectStatusEnum.CLOSED), None)),
    ]
    for i, (status, priority, defect) in enumerate(ncr_plans):
        rework_cost = Decimal(str(round(random.uniform(50, 800), 2)))
        scrap_cost = Decimal(str(round(random.uniform(0, 300), 2)))
        ncr = NonConformanceReport(
            ncr_number=f"NCR-{TODAY.strftime('%Y%m%d')}-{i+1:04d}",
            defect_id=defect.id if defect else None,
            manufacturing_order_id=defect.manufacturing_order_id if defect else None,
            status=status,
            priority=priority,
            description=fake.paragraph(nb_sentences=3),
            root_cause=fake.sentence(nb_words=15) if status != NCRStatusEnum.OPEN else None,
            root_cause_category=random.choice(["Method", "Material", "Machine", "Man", "Measurement"]) if status != NCRStatusEnum.OPEN else None,
            containment_actions="100% inspection of affected lot; segregate WIP." if status != NCRStatusEnum.OPEN else None,
            disposition=DispositionEnum.REWORK if status == NCRStatusEnum.PENDING_APPROVAL else (DispositionEnum.SCRAP if status == NCRStatusEnum.CLOSED else None),
            disposition_justification=fake.sentence(nb_words=14) if status != NCRStatusEnum.OPEN else None,
            quantity_affected=defect.quantity_affected if defect else 1,
            rework_cost=rework_cost,
            scrap_cost=scrap_cost,
            total_cost=rework_cost + scrap_cost,
            owner_id=users["qa_eng_1"].id,
            created_by_id=users["qa_eng_2"].id,
            approver_id=users["ops_mgr"].id if status in (NCRStatusEnum.APPROVED, NCRStatusEnum.CLOSED) else None,
            approval_date=days_ago(random.randint(1, 10)) if status == NCRStatusEnum.CLOSED else None,
            closed_by_id=users["qa_eng_1"].id if status == NCRStatusEnum.CLOSED else None,
            closed_date=days_ago(random.randint(1, 6)) if status == NCRStatusEnum.CLOSED else None,
        )
        session.add(ncr)
        ncrs.append(ncr)
    await session.flush()

    # CAPAs: 2 — one for the open critical NCR, one preventive
    capas: list[CorrectiveAction] = [
        CorrectiveAction(
            capa_number=f"CAPA-{TODAY.strftime('%Y%m%d')}-0001",
            ncr_id=ncrs[0].id,
            defect_id=critical_defect.id if critical_defect else None,
            action_type=ActionTypeEnum.CORRECTIVE,
            status=CAPAStatusEnum.IN_PROGRESS,
            priority=PriorityEnum.URGENT,
            problem_statement="Critical defect identified at in-process inspection; production blocked on affected MO.",
            root_cause="Solder reflow profile drift on SMT line — peak temperature below spec.",
            root_cause_method="5_whys",
            corrective_actions=[
                {"id": "1", "description": "Re-calibrate reflow oven, re-validate profile", "owner_id": users["ops_mgr"].id, "due_date": str((TODAY).isoformat()), "status": "in_progress"},
                {"id": "2", "description": "Re-inspect all boards from last 48h", "owner_id": users["qa_eng_1"].id, "due_date": str((TODAY).isoformat()), "status": "in_progress"},
            ],
            preventive_actions=[
                {"id": "3", "description": "Add daily reflow profile log review", "owner_id": users["qa_eng_2"].id, "due_date": "2026-06-01", "status": "open"},
            ],
            owner_id=users["qa_eng_1"].id,
            created_by_id=users["qa_eng_2"].id,
        ),
        CorrectiveAction(
            capa_number=f"CAPA-{TODAY.strftime('%Y%m%d')}-0002",
            ncr_id=ncrs[2].id if len(ncrs) > 2 else None,
            action_type=ActionTypeEnum.PREVENTIVE,
            status=CAPAStatusEnum.VERIFICATION,
            priority=PriorityEnum.NORMAL,
            problem_statement="Recurring cosmetic defects on enclosure paint finish.",
            root_cause="Inadequate cleaning step pre-paint.",
            root_cause_method="fishbone",
            corrective_actions=[
                {"id": "1", "description": "Add solvent wipe step", "owner_id": users["qa_eng_1"].id, "due_date": "2026-05-01", "status": "completed"},
            ],
            preventive_actions=[
                {"id": "2", "description": "Update enclosure SOP rev B", "owner_id": users["qa_eng_2"].id, "due_date": "2026-05-08", "status": "completed"},
            ],
            owner_id=users["qa_eng_2"].id,
            created_by_id=users["qa_eng_1"].id,
            verified_by_id=users["ops_mgr"].id,
            verification_date=days_ago(3),
            effectiveness_verification="Audit of last 80 units shows zero recurrence; SPC chart in control.",
        ),
    ]
    session.add_all(capas)

    # Quality Hold — the critical issue blocks the MO
    holds: list[QualityHold] = []
    if blocked_mo and critical_defect and ncrs:
        holds.append(QualityHold(
            hold_number=f"QH-{TODAY.strftime('%Y%m%d')}-0001",
            ncr_id=ncrs[0].id,
            hold_type=HoldTypeEnum.MANUFACTURING_ORDER,
            manufacturing_order_id=blocked_mo.id,
            status=HoldStatusEnum.ACTIVE,
            reason="Pending NCR review and disposition for critical defect — rework or scrap decision required.",
            quantity_held=blocked_mo.quantity,
            placed_by_id=users["qa_eng_1"].id,
            placed_date=days_ago(2),
        ))
    session.add_all(holds)

    await session.flush()

    print(
        f"  quality: {len(inspection_points)} inspection points, {len(inspection_results)} inspections, "
        f"{len(defects)} defects, {len(ncrs)} NCRs, {len(capas)} CAPAs, {len(holds)} holds"
    )

    return {
        "inspection_points": inspection_points,
        "inspection_results": inspection_results,
        "defects": defects,
        "ncrs": ncrs,
        "capas": capas,
        "holds": holds,
    }
