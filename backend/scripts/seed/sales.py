"""Sales seed: customers, RFQs, quotations, sales orders (with realistic lifecycle mix)."""
from datetime import timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import (
    Customer,
    Quotation,
    QuotationItem,
    QuotationStatusEnum,
    RFQ,
    RFQItem,
    RFQStatusEnum,
    SalesOrder,
    SalesOrderItem,
    SalesOrderStatusEnum,
)

from scripts.seed._session import fake, random
from scripts.seed._timeline import NOW, TODAY, date_ago, date_ahead, days_ago


CUSTOMER_TEMPLATES = [
    ("Lanka Solar Innovations",   "biz@lankasolar.lk",     "Colombo"),
    ("Galle Rural Power Co-op",   "ops@gallepower.lk",     "Galle"),
    ("Hill Country Energy",       "info@hcenergy.lk",      "Nuwara Eliya"),
    ("Jaffna Off-Grid Solutions", "sales@jaffnaog.lk",     "Jaffna"),
    ("Eastern Backup Systems",    "orders@ebsystems.lk",   "Batticaloa"),
    ("Kandy Reliable Power",      "team@krpower.lk",       "Kandy"),
    ("Negombo Marine Electric",   "service@nmemarine.lk",  "Negombo"),
    ("Anuradhapura Heritage Energy", "contact@ahenergy.lk", "Anuradhapura"),
    ("Trincomalee Coast Power",   "biz@tcpower.lk",        "Trincomalee"),
    ("Nuwara Eliya Tea Estates Power", "fac@netep.lk",     "Nuwara Eliya"),
    ("Matara Fishery Cooperative", "ops@mfcoop.lk",        "Matara"),
    ("Kurunegala Industrial Park", "estate@kip.lk",        "Kurunegala"),
    ("Ratnapura Gem Workshops",   "manager@rgws.lk",       "Ratnapura"),
    ("Hambantota Port Authority", "logistics@hpa.lk",      "Hambantota"),
    ("Polonnaruwa Farmers Union", "secretary@pfu.lk",      "Polonnaruwa"),
    ("Badulla Mountain Resorts",  "engineering@bmr.lk",    "Badulla"),
    ("Vavuniya Health Clinics",   "facilities@vhc.lk",     "Vavuniya"),
    ("Mannar Wind Auxiliary",     "ops@mwa.lk",            "Mannar"),
    ("Puttalam Salt Refineries",  "biz@psr.lk",            "Puttalam"),
    ("Ampara Rice Mills",         "contact@ampararm.lk",   "Ampara"),
    ("Colombo Hospital Trust",    "facilities@cht.lk",     "Colombo"),
    ("Western Telecom Towers",    "energy@wtt.lk",         "Colombo"),
    ("Southern Coast Resorts Ltd","fac@scrhotels.lk",      "Galle"),
    ("Sabaragamuwa Tea Pvt",      "ops@sabtea.lk",         "Ratnapura"),
    ("Uva Province Cold Storage", "biz@uvacold.lk",        "Badulla"),
]


# Status distribution for SOs across 60 orders (sums to 60)
SO_STATUS_PLAN = [
    (SalesOrderStatusEnum.DELIVERED,            18),
    (SalesOrderStatusEnum.READY_TO_SHIP,        12),
    (SalesOrderStatusEnum.IN_PRODUCTION,        12),
    (SalesOrderStatusEnum.PRODUCTION_SCHEDULED, 5),
    (SalesOrderStatusEnum.PROCESSING,           2),
    (SalesOrderStatusEnum.CONFIRMED,            2),
    (SalesOrderStatusEnum.PENDING,              6),
    (SalesOrderStatusEnum.CANCELLED,            3),
]


def _so_age_days(status: SalesOrderStatusEnum) -> int:
    """Order placement age — older orders are further along in lifecycle."""
    return {
        SalesOrderStatusEnum.DELIVERED:            random.randint(45, 90),
        SalesOrderStatusEnum.READY_TO_SHIP:        random.randint(20, 45),
        SalesOrderStatusEnum.IN_PRODUCTION:        random.randint(10, 35),
        SalesOrderStatusEnum.PRODUCTION_SCHEDULED: random.randint(5, 15),
        SalesOrderStatusEnum.PROCESSING:           random.randint(3, 10),
        SalesOrderStatusEnum.CONFIRMED:            random.randint(2, 7),
        SalesOrderStatusEnum.PENDING:              random.randint(0, 5),
        SalesOrderStatusEnum.CANCELLED:            random.randint(10, 60),
    }[status]


def _so_delivery_offset(status: SalesOrderStatusEnum, placed_age_days: int) -> int | None:
    """Days from today the delivery_date should land. Negative = past, positive = future, None = not set."""
    if status == SalesOrderStatusEnum.DELIVERED:
        return -random.randint(1, max(1, placed_age_days - 30))
    if status == SalesOrderStatusEnum.READY_TO_SHIP:
        return random.randint(1, 7)
    if status == SalesOrderStatusEnum.IN_PRODUCTION:
        return random.randint(5, 25)
    if status == SalesOrderStatusEnum.PRODUCTION_SCHEDULED:
        return random.randint(10, 30)
    if status == SalesOrderStatusEnum.PROCESSING:
        return random.randint(15, 35)
    if status == SalesOrderStatusEnum.CONFIRMED:
        return random.randint(20, 40)
    if status == SalesOrderStatusEnum.PENDING:
        return random.randint(25, 45)
    return None


async def seed(session: AsyncSession, refs: dict) -> dict:
    users = refs["users"]
    products = refs["products"]
    sales_reps = [users["sales_rep_1"], users["sales_rep_2"], users["sales_mgr"]]
    product_keys = list(products.keys())

    customers: list[Customer] = []
    for name, email, city in CUSTOMER_TEMPLATES:
        c = Customer(
            name=name,
            email=email,
            phone=f"+94 {fake.msisdn()[3:12]}",
            street_address=fake.street_address(),
            city=city,
            is_active=True,
            notes=fake.sentence(nb_words=8) if random.random() < 0.4 else None,
        )
        session.add(c)
        customers.append(c)
    await session.flush()

    # RFQs: 30 total
    rfqs: list[RFQ] = []
    rfq_status_mix = (
        [RFQStatusEnum.COMPLETED] * 18
        + [RFQStatusEnum.SENT] * 6
        + [RFQStatusEnum.DRAFT] * 3
        + [RFQStatusEnum.CANCELLED] * 3
    )
    random.shuffle(rfq_status_mix)
    for status in rfq_status_mix:
        age = random.randint(5, 100)
        rfq = RFQ(
            creator_id=random.choice(sales_reps).id,
            status=status,
            due_date=days_ago(age - random.randint(7, 21)),
            description=fake.paragraph(nb_sentences=2),
        )
        session.add(rfq)
        rfqs.append(rfq)
    await session.flush()

    rfq_items: list[RFQItem] = []
    for rfq in rfqs:
        for _ in range(random.randint(1, 3)):
            product = products[random.choice(product_keys)]
            rfq_items.append(RFQItem(
                rfq_id=rfq.id,
                product_id=product.id,
                quantity=random.randint(1, 8),
                unit_price=product.price * Decimal("0.95"),  # 5% discount on RFQ
            ))
    session.add_all(rfq_items)

    # Quotations: ~40 total, mostly traced to a COMPLETED RFQ
    completed_rfqs = [r for r in rfqs if r.status == RFQStatusEnum.COMPLETED]
    quotations: list[Quotation] = []
    quotation_status_mix = (
        [QuotationStatusEnum.ACCEPTED] * 24
        + [QuotationStatusEnum.QUOTATION_SENT] * 6
        + [QuotationStatusEnum.REJECTED] * 4
        + [QuotationStatusEnum.EXPIRED] * 3
        + [QuotationStatusEnum.QUOTATION] * 3
    )
    random.shuffle(quotation_status_mix)
    for i, status in enumerate(quotation_status_mix):
        rfq_link = completed_rfqs[i] if i < len(completed_rfqs) and random.random() < 0.7 else None
        cust = random.choice(customers)
        placed_age = random.randint(2, 95)
        q = Quotation(
            customer_id=cust.id,
            rfq_id=rfq_link.id if rfq_link else None,
            date=date_ago(placed_age),
            expiration_date=date_ago(placed_age) + timedelta(days=30),
            invoicing_and_shipping_address=f"{cust.street_address}, {cust.city}, Sri Lanka",
            total_amount=Decimal("0.00"),
            status=status,
            created_by_id=random.choice(sales_reps).id,
            email_sent_at=days_ago(placed_age - 1) if status != QuotationStatusEnum.QUOTATION else None,
            email_sent_count=1 if status != QuotationStatusEnum.QUOTATION else 0,
        )
        session.add(q)
        quotations.append(q)
    await session.flush()

    for q in quotations:
        total = Decimal("0.00")
        for _ in range(random.randint(1, 3)):
            product = products[random.choice(product_keys)]
            qty = random.randint(1, 6)
            unit_price = product.price
            session.add(QuotationItem(
                quotation_id=q.id,
                product_id=product.id,
                quantity=qty,
                unit_price=unit_price,
            ))
            total += unit_price * qty
        q.total_amount = total

    # Sales orders: 60 total, distributed per SO_STATUS_PLAN, some linked to accepted quotations
    sales_orders: list[SalesOrder] = []
    sales_order_items: list[SalesOrderItem] = []
    accepted_quotations = [q for q in quotations if q.status == QuotationStatusEnum.ACCEPTED]
    accepted_iter = iter(accepted_quotations)

    so_plan: list[SalesOrderStatusEnum] = []
    for status, count in SO_STATUS_PLAN:
        so_plan.extend([status] * count)
    random.shuffle(so_plan)

    for status in so_plan:
        age = _so_age_days(status)
        # quotation linkage: ~70% of in-production-or-later orders trace to an accepted quotation
        link_q = None
        if status not in (SalesOrderStatusEnum.PENDING, SalesOrderStatusEnum.CANCELLED) and random.random() < 0.7:
            link_q = next(accepted_iter, None)

        cust = link_q.customer if link_q else random.choice(customers)
        delivery_offset = _so_delivery_offset(status, age)
        delivery_date = (NOW + timedelta(days=delivery_offset)) if delivery_offset is not None else None

        so = SalesOrder(
            customer_id=cust.id,
            quotation_id=link_q.id if link_q else None,
            total_amount=Decimal("0.00"),
            status=status,
            delivery_date=delivery_date,
        )
        session.add(so)
        sales_orders.append(so)
    await session.flush()

    # Now backfill SO items + totals + creation time
    for so in sales_orders:
        # If linked quotation, copy its items; otherwise generate fresh
        source_items: list[tuple[int, int, Decimal]] = []
        if so.quotation_id:
            quote = next((q for q in quotations if q.id == so.quotation_id), None)
            if quote is not None:
                qis = [qi for qi in session.new if isinstance(qi, QuotationItem) and qi.quotation_id == quote.id]
                if not qis:
                    # already flushed — look up from quotation.quotation_items if loaded
                    qis = []
                for qi in qis:
                    source_items.append((qi.product_id, qi.quantity, qi.unit_price))
        if not source_items:
            for _ in range(random.randint(1, 3)):
                product = products[random.choice(product_keys)]
                source_items.append((product.id, random.randint(1, 4), product.price))

        total = Decimal("0.00")
        for product_id, qty, price in source_items:
            session.add(SalesOrderItem(
                order_id=so.id,
                product_id=product_id,
                quantity=qty,
                price=price,
            ))
            total += price * qty
        so.total_amount = total

        # Backdate created_at via TimestampMixin
        so.created_at = days_ago(_so_age_days(so.status))
        so.updated_at = so.created_at + timedelta(days=random.randint(0, 2))
    await session.flush()

    print(
        f"  sales: {len(customers)} customers, {len(rfqs)} RFQs, "
        f"{len(quotations)} quotations, {len(sales_orders)} sales orders"
    )

    return {
        "customers": customers,
        "rfqs": rfqs,
        "quotations": quotations,
        "sales_orders": sales_orders,
    }
