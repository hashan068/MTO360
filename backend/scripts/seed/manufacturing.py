"""Manufacturing seed: MOs, MRs, MR items, operations, work center schedules, consumption."""
from datetime import date as _date_cls, datetime as _datetime_cls, timedelta, time
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import ConsumptionTransaction
from app.models.manufacturing import (
    BOMItem,
    ManufacturingOrder,
    ManufacturingOrderOperation,
    ManufacturingOrderStatusEnum,
    MaterialRequisition,
    MaterialRequisitionItem,
    MaterialRequisitionItemStatusEnum,
    MaterialRequisitionStatusEnum,
    OperationStatusEnum,
    RouteOperation,
    WorkCenterSchedule,
)
from app.models.sales import SalesOrder, SalesOrderItem, SalesOrderStatusEnum

from scripts.seed._session import random
from scripts.seed._timeline import (
    HORIZON_FUTURE_DAYS,
    HORIZON_PAST_DAYS,
    NOW,
    TODAY,
    WINDOW_END,
    WINDOW_START,
    days_ago,
    days_ahead,
)


# Map sales order status → manufacturing order status + how complete operations should be
SO_TO_MO_STATE = {
    SalesOrderStatusEnum.DELIVERED:            (ManufacturingOrderStatusEnum.COMPLETED,    "all_done"),
    SalesOrderStatusEnum.READY_TO_SHIP:        (ManufacturingOrderStatusEnum.COMPLETED,    "all_done"),
    SalesOrderStatusEnum.IN_PRODUCTION:        (ManufacturingOrderStatusEnum.IN_PRODUCTION,"in_progress"),
    SalesOrderStatusEnum.PRODUCTION_SCHEDULED: (ManufacturingOrderStatusEnum.MR_APPROVED,  "scheduled"),
    SalesOrderStatusEnum.PROCESSING:           (ManufacturingOrderStatusEnum.MR_SENT,      "pending"),
    SalesOrderStatusEnum.CONFIRMED:            (ManufacturingOrderStatusEnum.PENDING,      "pending"),
}


def _bom_for_route(route_key: str, route_ops_by_family, bom_items_by_bom) -> tuple[int, list[tuple[int, int]]]:
    """Return (bom_id, [(component_id, qty)]) for given family route_key."""
    return bom_items_by_bom[route_key]


async def seed(session: AsyncSession, refs: dict) -> dict:
    users = refs["users"]
    products = refs["products"]
    family_of_product = refs["family_of_product"]
    routes = refs["routes"]
    route_ops_by_family = refs["route_ops_by_family"]
    boms = refs["boms"]
    components_by_name = refs["components"]
    work_centers = refs["work_centers"]
    sales_orders: list[SalesOrder] = refs["sales_orders"]

    operators = [users["operator_1"], users["operator_2"]]
    planner = users["planner"]

    from sqlalchemy import select as _select

    so_items_by_so: dict[int, list[SalesOrderItem]] = {so.id: [] for so in sales_orders}
    so_items_q = await session.execute(_select(SalesOrderItem))
    for soi in so_items_q.scalars():
        so_items_by_so.setdefault(soi.order_id, []).append(soi)

    # Pre-build product → (bom_id, [(component_id, qty)]) lookup
    bom_items_q = await session.execute(_select(BOMItem))
    bom_items_by_bom_id: dict[int, list[tuple[int, int]]] = {}
    for bi in bom_items_q.scalars():
        bom_items_by_bom_id.setdefault(bi.bill_of_material_id, []).append((bi.component_id, bi.quantity))

    # Lookup family bom by route_key → bom.id
    bom_id_by_family = {rk: b.id for rk, b in boms.items()}

    manufacturing_orders: list[ManufacturingOrder] = []
    mo_operations: list[ManufacturingOrderOperation] = []
    material_reqs: list[MaterialRequisition] = []
    mr_items: list[MaterialRequisitionItem] = []
    consumption_txs: list[ConsumptionTransaction] = []
    in_progress_mo_for_quality_hold: ManufacturingOrder | None = None

    schedule_load: dict[tuple[int, _date_cls], int] = {}

    def _record_load(wc_id: int, start: _datetime_cls, minutes: int) -> None:
        d = start.date()
        schedule_load[(wc_id, d)] = schedule_load.get((wc_id, d), 0) + minutes

    # Find product key from product id
    product_id_to_key = {p.id: k for k, p in products.items()}

    for so in sales_orders:
        if so.status not in SO_TO_MO_STATE:
            continue  # PENDING or CANCELLED → no MO
        mo_status, op_profile = SO_TO_MO_STATE[so.status]
        so_age = (NOW - so.created_at).days if so.created_at else 30
        for soi in so_items_by_so.get(so.id, []):
            product_key = product_id_to_key.get(soi.product_id)
            if not product_key:
                continue
            family_key = family_of_product[product_key]
            route = routes[family_key]
            route_ops = route_ops_by_family[family_key]
            bom_id = bom_id_by_family[family_key]
            bom_lines = bom_items_by_bom_id.get(bom_id, [])

            # Total operation duration
            total_op_minutes = sum(ro.standard_time_minutes + ro.setup_time_minutes for ro in route_ops) * soi.quantity

            mo = ManufacturingOrder(
                sales_order_item_id=soi.id,
                product_id=soi.product_id,
                quantity=soi.quantity,
                bom_id=bom_id,
                status=mo_status,
                creator_id=planner.id,
                production_start_at=days_ago(so_age - 2) if op_profile != "pending" else None,
                end_at=days_ago(max(1, so_age - 12)) if op_profile == "all_done" else None,
                estimated_mfg_lead_time=timedelta(days=10),
                mfg_lead_time=timedelta(days=random.randint(8, 14)) if op_profile == "all_done" else None,
                production_lead_time=timedelta(days=random.randint(8, 12)) if op_profile == "all_done" else None,
                scheduled_start=days_ago(so_age - 2) if op_profile != "pending" else None,
                scheduled_end=days_ago(max(1, so_age - 12)) if op_profile == "all_done" else (days_ahead(random.randint(3, 20)) if op_profile in ("scheduled", "in_progress") else None),
                total_scheduled_duration_minutes=total_op_minutes,
                quality_status="pass" if op_profile == "all_done" else None,
            )
            mo.created_at = days_ago(so_age - 1)
            mo.updated_at = mo.created_at + timedelta(hours=2)
            session.add(mo)
            manufacturing_orders.append(mo)
    await session.flush()

    # Now create child entities — MR, MR items, operations, schedules
    # (need MO ids, hence after flush)
    for mo in manufacturing_orders:
        so = next((s for s in sales_orders if any(soi.id == mo.sales_order_item_id for soi in so_items_by_so.get(s.id, []))), None)
        if so is None:
            continue
        op_profile = SO_TO_MO_STATE[so.status][1]
        product_key = product_id_to_key[mo.product_id]
        family_key = family_of_product[product_key]
        route_ops = route_ops_by_family[family_key]
        bom_lines = bom_items_by_bom_id.get(mo.bom_id, [])

        # Material Requisition
        if op_profile == "pending":
            mr_status = MaterialRequisitionStatusEnum.PENDING
            item_status = MaterialRequisitionItemStatusEnum.PENDING
            consumed = False
        elif op_profile in ("scheduled", "in_progress", "all_done"):
            mr_status = MaterialRequisitionStatusEnum.FULFILLED
            item_status = MaterialRequisitionItemStatusEnum.APPROVED
            consumed = op_profile in ("in_progress", "all_done")
        else:
            mr_status = MaterialRequisitionStatusEnum.APPROVED
            item_status = MaterialRequisitionItemStatusEnum.APPROVED
            consumed = False

        mr = MaterialRequisition(
            manufacturing_order_id=mo.id,
            bom_id=mo.bom_id,
            status=mr_status,
        )
        mr.created_at = mo.created_at + timedelta(hours=4)
        mr.updated_at = mr.created_at + timedelta(days=1)
        session.add(mr)
        await session.flush()
        material_reqs.append(mr)

        for component_id, per_unit_qty in bom_lines:
            req_qty = per_unit_qty * mo.quantity
            mri = MaterialRequisitionItem(
                material_requisition_id=mr.id,
                component_id=component_id,
                quantity=req_qty,
                status=item_status,
            )
            session.add(mri)
            mr_items.append(mri)
            if consumed:
                # Consumption transaction recorded at production start
                await session.flush()  # so mri.id is real
                consumption_txs.append(ConsumptionTransaction(
                    material_requisition_item_id=mri.id,
                    component_id=component_id,
                    quantity=req_qty,
                    user_id=random.choice(operators).id,
                    timestamp=mo.production_start_at or days_ago(5),
                ))

        # Operations
        op_count = len(route_ops)
        op_states: list[OperationStatusEnum] = []
        if op_profile == "all_done":
            op_states = [OperationStatusEnum.COMPLETED] * op_count
        elif op_profile == "in_progress":
            # First N completed, current in_progress, rest scheduled
            current_idx = random.randint(1, op_count - 2) if op_count > 2 else 0
            for i in range(op_count):
                if i < current_idx:
                    op_states.append(OperationStatusEnum.COMPLETED)
                elif i == current_idx:
                    op_states.append(OperationStatusEnum.IN_PROGRESS)
                else:
                    op_states.append(OperationStatusEnum.SCHEDULED)
        elif op_profile == "scheduled":
            op_states = [OperationStatusEnum.SCHEDULED] * op_count
        else:
            op_states = [OperationStatusEnum.PENDING] * op_count

        anchor = mo.production_start_at or mo.scheduled_start or days_ahead(7)
        cursor_dt = anchor.replace(hour=9, minute=0, second=0, microsecond=0) if anchor else None
        for idx, ro in enumerate(route_ops):
            state = op_states[idx]
            duration = (ro.standard_time_minutes + ro.setup_time_minutes) * mo.quantity
            start_dt = cursor_dt
            end_dt = cursor_dt + timedelta(minutes=duration) if cursor_dt else None

            actual_start = None
            actual_end = None
            actual_dur = None
            if state == OperationStatusEnum.COMPLETED:
                actual_start = start_dt
                actual_end = end_dt
                actual_dur = duration + random.randint(-15, 30)
            elif state == OperationStatusEnum.IN_PROGRESS:
                actual_start = start_dt
            scheduled = state in (
                OperationStatusEnum.SCHEDULED,
                OperationStatusEnum.IN_PROGRESS,
                OperationStatusEnum.COMPLETED,
            )

            mop = ManufacturingOrderOperation(
                manufacturing_order_id=mo.id,
                route_operation_id=ro.id,
                sequence=ro.sequence,
                name=ro.name,
                work_center_id=ro.work_center_id,
                scheduled_start=start_dt if scheduled else None,
                scheduled_end=end_dt if scheduled else None,
                scheduled_duration_minutes=duration,
                actual_start=actual_start,
                actual_end=actual_end,
                actual_duration_minutes=actual_dur,
                status=state,
                assigned_operator_id=random.choice(operators).id if scheduled else None,
                inspection_status="pass" if state == OperationStatusEnum.COMPLETED else None,
                quality_hold=False,
            )
            mop.created_at = mo.created_at + timedelta(hours=6)
            mop.updated_at = (actual_end or end_dt or mop.created_at)
            session.add(mop)
            mo_operations.append(mop)

            if scheduled and start_dt is not None:
                _record_load(ro.work_center_id, start_dt, duration)

            # Advance cursor; if duration overflows day, push to next business morning
            if cursor_dt and end_dt:
                if end_dt.hour >= 17:
                    cursor_dt = (end_dt + timedelta(days=1)).replace(hour=9, minute=0)
                    while cursor_dt.weekday() >= 5:
                        cursor_dt += timedelta(days=1)
                else:
                    cursor_dt = end_dt + timedelta(minutes=10)

    await session.flush()

    # Pick one IN_PRODUCTION MO to block on a critical quality issue (referenced from quality seed)
    candidates = [mo for mo in manufacturing_orders if mo.status == ManufacturingOrderStatusEnum.IN_PRODUCTION]
    if candidates:
        block_mo = candidates[0]
        block_mo.status = ManufacturingOrderStatusEnum.BLOCKED
        block_mo.quality_status = "fail"
        # Mark the in-progress operation as blocked
        ops_q = await session.execute(
            _select(ManufacturingOrderOperation)
            .where(ManufacturingOrderOperation.manufacturing_order_id == block_mo.id)
            .where(ManufacturingOrderOperation.status == OperationStatusEnum.IN_PROGRESS)
        )
        for op in ops_q.scalars():
            op.status = OperationStatusEnum.BLOCKED
            op.quality_hold = True
            op.blocking_reason = "Critical defect found during in-process inspection — pending NCR review"
        in_progress_mo_for_quality_hold = block_mo
    await session.flush()

    # Work center schedules — 6 centers × 90 days past + 30 future
    schedules: list[WorkCenterSchedule] = []
    cap_per_day_by_wc = {wc.id: int(wc.capacity_hours_per_day * 60) for wc in work_centers.values()}
    cursor_d = WINDOW_START
    while cursor_d <= WINDOW_END:
        weekday_factor = 0.7 if cursor_d.weekday() == 0 else (1.0 if cursor_d.weekday() < 5 else 0.0)
        for wc in work_centers.values():
            available = int(cap_per_day_by_wc[wc.id] * weekday_factor) if weekday_factor > 0 else 0
            scheduled = schedule_load.get((wc.id, cursor_d), 0)
            if available <= 0 and scheduled > 0:
                available = scheduled  # avoid /0
            util = Decimal(0)
            if available > 0:
                util = (Decimal(scheduled) / Decimal(available) * Decimal(100)).quantize(Decimal("0.01"))
            schedules.append(WorkCenterSchedule(
                work_center_id=wc.id,
                date=cursor_d,
                available_capacity_minutes=available,
                scheduled_capacity_minutes=scheduled,
                utilization_percentage=util,
            ))
        cursor_d += timedelta(days=1)
    session.add_all(schedules)

    # Component consumption: write transactions; later component.quantity adjustment is recalculated
    session.add_all(consumption_txs)
    await session.flush()

    # Now recompute on-hand quantities = initial − consumed (replenish happens in procurement seed)
    consumed_by_component: dict[int, int] = {}
    for tx in consumption_txs:
        consumed_by_component[tx.component_id] = consumed_by_component.get(tx.component_id, 0) + tx.quantity
    refs["consumed_by_component"] = consumed_by_component

    print(
        f"  manufacturing: {len(manufacturing_orders)} MOs, {len(material_reqs)} MRs, "
        f"{len(mr_items)} MR items, {len(mo_operations)} operations, "
        f"{len(schedules)} WC-schedule rows, {len(consumption_txs)} consumption txs"
    )

    return {
        "manufacturing_orders": manufacturing_orders,
        "mo_operations": mo_operations,
        "material_requisitions": material_reqs,
        "mr_items": mr_items,
        "blocked_mo": in_progress_mo_for_quality_hold,
    }
