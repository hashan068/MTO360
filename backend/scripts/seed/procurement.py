"""Procurement seed: PRs, POs, replenish, contracts, supplier performance, RFQs, policies, forecasts."""
from datetime import timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import (
    PriorityEnum,
    PurchaseOrder,
    PurchaseOrderStatusEnum,
    PurchaseRequisition,
    ReplenishTransaction,
    StatusEnum,
)
from app.models.procurement import (
    ABCClassificationEnum,
    ComponentInventoryPolicy,
    ComponentPriceHistory,
    ContractPricing,
    ContractStatusEnum,
    DemandForecast,
    ForecastMethodEnum,
    PriceChangeSourceEnum,
    ProcurementBudget,
    ProcurementRFQ,
    ProcurementRFQStatusEnum,
    SupplierContract,
    SupplierPerformance,
    SupplierQuote,
    SupplierQuoteStatusEnum,
)

from scripts.seed._session import fake, random
from scripts.seed._timeline import NOW, TODAY, date_ago, date_ahead, days_ago, days_ahead


PO_STATUS_PLAN = [
    (PurchaseOrderStatusEnum.RECEIVED, 20),
    (PurchaseOrderStatusEnum.APPROVED, 15),
    (PurchaseOrderStatusEnum.OPEN_ORDER, 10),
    (PurchaseOrderStatusEnum.DRAFT, 5),
]


async def seed(session: AsyncSession, refs: dict) -> dict:
    users = refs["users"]
    suppliers = refs["suppliers"]
    components = refs["components"]
    categories = refs["categories"]
    consumed_by_component: dict[int, int] = refs.get("consumed_by_component", {})

    proc_mgr = users["proc_mgr"]
    component_list = list(components.values())

    # Purchase Requisitions: 80 total, statuses biased by component depletion
    prs: list[PurchaseRequisition] = []
    pr_status_mix = (
        [StatusEnum.FULFILLED] * 35
        + [StatusEnum.APPROVED] * 20
        + [StatusEnum.PENDING] * 15
        + [StatusEnum.REJECTED] * 5
        + [StatusEnum.CANCELLED] * 5
    )
    random.shuffle(pr_status_mix)
    for status in pr_status_mix:
        comp = random.choice(component_list)
        age = random.randint(2, 88)
        priority = random.choices(
            [PriorityEnum.HIGH, PriorityEnum.MEDIUM, PriorityEnum.LOW],
            weights=[3, 5, 2],
        )[0]
        pr = PurchaseRequisition(
            user_id=proc_mgr.id,
            component_id=comp.id,
            quantity=comp.reorder_quantity if comp.reorder_quantity else 100,
            status=status,
            notes=f"Replenishment for {comp.name}",
            expected_delivery_date=days_ahead(random.randint(5, 21)) if status in (StatusEnum.PENDING, StatusEnum.APPROVED) else days_ago(random.randint(1, 30)),
            priority=priority,
        )
        pr.created_at = days_ago(age)
        pr.updated_at = pr.created_at + timedelta(days=random.randint(0, 5))
        session.add(pr)
        prs.append(pr)
    await session.flush()

    # Purchase Orders: 50 total, derived from approved/fulfilled PRs
    candidate_prs = [pr for pr in prs if pr.status in (StatusEnum.APPROVED, StatusEnum.FULFILLED)]
    random.shuffle(candidate_prs)
    po_status_pool: list[PurchaseOrderStatusEnum] = []
    for status, count in PO_STATUS_PLAN:
        po_status_pool.extend([status] * count)
    random.shuffle(po_status_pool)

    purchase_orders: list[PurchaseOrder] = []
    replenishes: list[ReplenishTransaction] = []
    price_history: list[ComponentPriceHistory] = []
    for po_status, pr in zip(po_status_pool, candidate_prs):
        comp = next(c for c in component_list if c.id == pr.component_id)
        supplier = next((s for s in suppliers if s.id == comp.supplier_id), random.choice(suppliers))
        # Per-PR price = component cost ± 5%
        unit_price = (comp.cost * Decimal(str(round(random.uniform(0.95, 1.05), 3)))).quantize(Decimal("0.01"))
        total = (unit_price * pr.quantity).quantize(Decimal("0.01"))
        age = max(1, (NOW - pr.created_at).days - random.randint(1, 4))
        po = PurchaseOrder(
            creator_id=proc_mgr.id,
            purchase_requisition_id=pr.id,
            supplier_id=supplier.id,
            status=po_status,
            notes=fake.sentence(nb_words=6),
            price_per_unit=unit_price,
            total_price=total,
        )
        po.created_at = days_ago(age)
        po.updated_at = po.created_at + timedelta(days=random.randint(0, 3))
        session.add(po)
        purchase_orders.append(po)
    await session.flush()

    # Replenish transactions + price history for RECEIVED POs
    for po in purchase_orders:
        if po.status != PurchaseOrderStatusEnum.RECEIVED:
            continue
        pr = next(p for p in prs if p.id == po.purchase_requisition_id)
        comp_id = pr.component_id
        recv_dt = po.created_at + timedelta(days=random.randint(5, 14))
        replenishes.append(ReplenishTransaction(
            purchase_requisition_id=pr.id,
            component_id=comp_id,
            quantity=pr.quantity,
            user_id=proc_mgr.id,
            timestamp=recv_dt,
        ))
        price_history.append(ComponentPriceHistory(
            component_id=comp_id,
            supplier_id=po.supplier_id,
            unit_price=po.price_per_unit,
            effective_date=recv_dt.date(),
            price_change_source=PriceChangeSourceEnum.PURCHASE_ORDER,
            purchase_order_id=po.id,
            recorded_by=proc_mgr.id,
            created_at=recv_dt,
        ))
    session.add_all(replenishes)
    session.add_all(price_history)

    # Apply on-hand quantity = initial − consumed + replenished
    replenished_by_component: dict[int, int] = {}
    for r in replenishes:
        replenished_by_component[r.component_id] = replenished_by_component.get(r.component_id, 0) + r.quantity
    for comp in component_list:
        delta = replenished_by_component.get(comp.id, 0) - consumed_by_component.get(comp.id, 0)
        comp.quantity = max(0, comp.quantity + delta)

    # Component Inventory Policies — one per component
    policies: list[ComponentInventoryPolicy] = []
    component_costs_sorted = sorted(component_list, key=lambda c: float(c.cost) * c.quantity, reverse=True)
    for idx, comp in enumerate(component_costs_sorted):
        # ABC: top 20% A, next 30% B, remaining C
        share = idx / len(component_costs_sorted)
        if share < 0.20:
            abc = ABCClassificationEnum.A
        elif share < 0.50:
            abc = ABCClassificationEnum.B
        else:
            abc = ABCClassificationEnum.C
        monthly_demand = max(10, int(consumed_by_component.get(comp.id, comp.reorder_quantity or 50) / 3))
        lead = random.randint(5, 21)
        safety = int(monthly_demand * 0.4)
        rop = int((monthly_demand / 30) * lead + safety)
        eoq = max(comp.reorder_quantity or 100, int((monthly_demand * 12) ** 0.5 * 10))
        policies.append(ComponentInventoryPolicy(
            component_id=comp.id,
            reorder_point=rop,
            safety_stock=safety,
            economic_order_quantity=eoq,
            abc_classification=abc,
            average_monthly_demand=monthly_demand,
            lead_time_days=lead,
            ordering_cost=Decimal("75.00") if abc == ABCClassificationEnum.A else Decimal("50.00"),
            holding_cost_pct=Decimal("25.00"),
            auto_pr_enabled=(abc != ABCClassificationEnum.C),
            updated_by=proc_mgr.id,
            last_calculated_at=days_ago(random.randint(1, 14)),
        ))
    session.add_all(policies)

    # Demand Forecasts — next 6 months × every component
    forecasts: list[DemandForecast] = []
    forecast_methods = list(ForecastMethodEnum)
    today_first = TODAY.replace(day=1)
    for comp in component_list:
        monthly = max(20, int(consumed_by_component.get(comp.id, comp.reorder_quantity or 60) / 3))
        method = random.choice(forecast_methods)
        for m in range(6):
            yr = today_first.year + (today_first.month + m - 1) // 12
            mo = ((today_first.month + m - 1) % 12) + 1
            forecast_dt = today_first.replace(year=yr, month=mo, day=1)
            seasonal = 1.0 + 0.15 * (m / 6)
            forecasts.append(DemandForecast(
                component_id=comp.id,
                forecast_month=forecast_dt,
                forecasted_demand=int(monthly * seasonal * random.uniform(0.9, 1.1)),
                actual_demand=int(monthly * random.uniform(0.85, 1.05)) if m == 0 else None,
                forecast_method=method,
                forecast_accuracy_mape=Decimal(str(round(random.uniform(5, 18), 2))) if m == 0 else None,
            ))
    session.add_all(forecasts)

    # Supplier Contracts — 10 (8 active, 2 expired)
    contracts: list[SupplierContract] = []
    contract_lines: list[ContractPricing] = []
    for i, supplier in enumerate(suppliers):
        is_expired = i >= 8
        start = date_ago(random.randint(180, 540))
        end = date_ago(random.randint(5, 45)) if is_expired else date_ahead(random.randint(60, 540))
        status = ContractStatusEnum.EXPIRED if is_expired else ContractStatusEnum.ACTIVE
        contract = SupplierContract(
            contract_number=f"CONTRACT-2026-{i+1:04d}",
            supplier_id=supplier.id,
            start_date=start,
            end_date=end,
            payment_terms=random.choice(["Net 30", "Net 45", "Net 60"]),
            volume_discounts=[
                {"min_qty": 100, "max_qty": 499, "discount_pct": 3},
                {"min_qty": 500, "max_qty": 999, "discount_pct": 6},
                {"min_qty": 1000, "max_qty": None, "discount_pct": 10},
            ],
            status=status,
            auto_renew=(not is_expired and random.random() < 0.4),
            renewal_notice_days=90,
            created_by=proc_mgr.id,
            approved_by=users["admin"].id,
            approved_at=days_ago(random.randint(180, 540) - 5),
        )
        session.add(contract)
        contracts.append(contract)
    await session.flush()

    # Contract pricing: each contract covers 3-6 components from this supplier
    for contract in contracts:
        supplier_components = [c for c in component_list if c.supplier_id == contract.supplier_id]
        if not supplier_components:
            supplier_components = random.sample(component_list, k=min(4, len(component_list)))
        picks = random.sample(supplier_components, k=min(random.randint(3, 6), len(supplier_components)))
        for comp in picks:
            unit_price = (comp.cost * Decimal(str(round(random.uniform(0.88, 0.97), 3)))).quantize(Decimal("0.01"))
            contract_lines.append(ContractPricing(
                contract_id=contract.id,
                component_id=comp.id,
                unit_price=unit_price,
                minimum_order_quantity=max(50, comp.reorder_quantity // 4 if comp.reorder_quantity else 50),
                lead_time_days=random.randint(7, 21),
                effective_from=contract.start_date,
                effective_to=contract.end_date,
                is_active=(contract.status == ContractStatusEnum.ACTIVE),
            ))
    session.add_all(contract_lines)

    # Procurement RFQs (20) + Supplier Quotes (~50)
    proc_rfqs: list[ProcurementRFQ] = []
    proc_quotes: list[SupplierQuote] = []
    rfq_status_mix = (
        [ProcurementRFQStatusEnum.AWARDED] * 10
        + [ProcurementRFQStatusEnum.QUOTES_RECEIVED] * 4
        + [ProcurementRFQStatusEnum.SENT] * 3
        + [ProcurementRFQStatusEnum.DRAFT] * 2
        + [ProcurementRFQStatusEnum.CANCELLED] * 1
    )
    random.shuffle(rfq_status_mix)
    for i, status in enumerate(rfq_status_mix):
        comp = random.choice(component_list)
        age = random.randint(5, 70)
        required_by = date_ahead(random.randint(15, 60)) if status not in (ProcurementRFQStatusEnum.AWARDED, ProcurementRFQStatusEnum.CANCELLED) else date_ago(random.randint(1, 20))
        closing = days_ahead(random.randint(3, 14)) if status == ProcurementRFQStatusEnum.SENT else days_ago(random.randint(1, 50))
        rfq = ProcurementRFQ(
            rfq_number=f"PRFQ-2026-{i+1:04d}",
            component_id=comp.id,
            quantity=comp.reorder_quantity * random.choice([1, 2, 3]) if comp.reorder_quantity else random.randint(200, 1500),
            required_by_date=required_by,
            closing_datetime=closing,
            status=status,
            specifications=fake.paragraph(nb_sentences=3),
            internal_notes=fake.sentence(nb_words=10),
            created_by=proc_mgr.id,
            sent_at=days_ago(age - 1) if status != ProcurementRFQStatusEnum.DRAFT else None,
            awarded_at=days_ago(max(1, age - 15)) if status == ProcurementRFQStatusEnum.AWARDED else None,
            cancelled_at=days_ago(max(1, age - 5)) if status == ProcurementRFQStatusEnum.CANCELLED else None,
            cancellation_reason="Component sourced via existing contract" if status == ProcurementRFQStatusEnum.CANCELLED else None,
        )
        rfq.created_at = days_ago(age)
        rfq.updated_at = rfq.created_at + timedelta(days=2)
        session.add(rfq)
        proc_rfqs.append(rfq)
    await session.flush()

    # Quotes: 3 suppliers per non-draft RFQ
    for rfq in proc_rfqs:
        if rfq.status == ProcurementRFQStatusEnum.DRAFT:
            continue
        invited = random.sample(suppliers, k=3)
        base_price = (next(c for c in component_list if c.id == rfq.component_id).cost)
        prices = sorted(
            (base_price * Decimal(str(round(random.uniform(0.85, 1.15), 3)))).quantize(Decimal("0.01")) for _ in range(3)
        )
        for j, supplier in enumerate(invited):
            quote_status = SupplierQuoteStatusEnum.PENDING
            is_awarded = False
            submitted_at = None
            awarded_at = None
            justification = None
            if rfq.status in (ProcurementRFQStatusEnum.QUOTES_RECEIVED, ProcurementRFQStatusEnum.AWARDED):
                quote_status = SupplierQuoteStatusEnum.SUBMITTED
                submitted_at = rfq.sent_at + timedelta(days=random.randint(2, 7)) if rfq.sent_at else days_ago(15)
            if rfq.status == ProcurementRFQStatusEnum.AWARDED and j == 0:
                quote_status = SupplierQuoteStatusEnum.ACCEPTED
                is_awarded = True
                awarded_at = rfq.awarded_at
                justification = "Lowest unit price with acceptable lead time."
            elif rfq.status == ProcurementRFQStatusEnum.AWARDED:
                quote_status = SupplierQuoteStatusEnum.REJECTED
            proc_quotes.append(SupplierQuote(
                rfq_id=rfq.id,
                supplier_id=supplier.id,
                unit_price=prices[j],
                lead_time_days=random.randint(7, 28),
                minimum_order_quantity=max(50, rfq.quantity // 10),
                quote_valid_until=date_ahead(random.randint(15, 45)),
                notes=fake.sentence(nb_words=8),
                status=quote_status,
                is_awarded=is_awarded,
                submitted_at=submitted_at,
                awarded_at=awarded_at,
                award_justification=justification,
            ))
    session.add_all(proc_quotes)

    # Supplier Performance — last 3 months per supplier
    perf_records: list[SupplierPerformance] = []
    for supplier in suppliers:
        supplier_pos = [po for po in purchase_orders if po.supplier_id == supplier.id]
        for m in range(3):
            yr = today_first.year if today_first.month - m > 0 else today_first.year - 1
            mo = today_first.month - m if today_first.month - m > 0 else today_first.month - m + 12
            period = today_first.replace(year=yr, month=mo, day=1)
            relevant = [po for po in supplier_pos if po.created_at.month == period.month and po.created_at.year == period.year]
            received = [po for po in relevant if po.status == PurchaseOrderStatusEnum.RECEIVED]
            on_time = Decimal(str(round(random.uniform(75, 99), 2)))
            quality = Decimal(str(round(random.uniform(85, 100), 2)))
            lead_avg = random.randint(7, 18)
            price_score = Decimal(str(round(random.uniform(75, 95), 2)))
            spend = sum((po.total_price or Decimal(0)) for po in received)
            overall = (on_time * Decimal("0.3") + quality * Decimal("0.35") + price_score * Decimal("0.35")).quantize(Decimal("0.01"))
            perf_records.append(SupplierPerformance(
                supplier_id=supplier.id,
                period=period,
                on_time_delivery_rate=on_time,
                quality_rating=quality,
                average_lead_time_days=lead_avg,
                price_competitiveness_score=price_score,
                total_spend=Decimal(spend).quantize(Decimal("0.01")),
                overall_score=overall,
            ))
    session.add_all(perf_records)

    # Procurement Budgets — current fiscal year, per category + overall
    budgets: list[ProcurementBudget] = []
    fy = TODAY.year
    for cat in categories.values():
        budgeted = Decimal(random.randint(50_000, 250_000))
        actual = (budgeted * Decimal(str(round(random.uniform(0.4, 1.05), 3)))).quantize(Decimal("0.01"))
        variance = (budgeted - actual).quantize(Decimal("0.01"))
        variance_pct = (variance / budgeted * Decimal(100)).quantize(Decimal("0.01")) if budgeted else Decimal(0)
        budgets.append(ProcurementBudget(
            fiscal_year=fy,
            category_id=cat.id,
            budgeted_amount=budgeted,
            actual_spend=actual,
            variance=variance,
            variance_pct=variance_pct,
        ))
    budgets.append(ProcurementBudget(
        fiscal_year=fy,
        category_id=None,
        budgeted_amount=Decimal("1500000.00"),
        actual_spend=Decimal(sum(b.actual_spend for b in budgets)).quantize(Decimal("0.01")),
        variance=Decimal("0.00"),
        variance_pct=Decimal("0.00"),
    ))
    session.add_all(budgets)

    await session.flush()

    print(
        f"  procurement: {len(prs)} PRs, {len(purchase_orders)} POs, {len(replenishes)} replenishes, "
        f"{len(price_history)} price entries, {len(policies)} inv policies, {len(forecasts)} forecasts, "
        f"{len(contracts)} contracts, {len(contract_lines)} contract lines, "
        f"{len(proc_rfqs)} procurement RFQs, {len(proc_quotes)} supplier quotes, "
        f"{len(perf_records)} performance rows, {len(budgets)} budgets"
    )

    return {
        "purchase_requisitions": prs,
        "purchase_orders": purchase_orders,
        "supplier_contracts": contracts,
    }
