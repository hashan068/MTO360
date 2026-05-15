"""Notifications seed: recent activity per active user."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import (
    Notification,
    NotificationSeverityEnum,
    NotificationTypeEnum,
)

from scripts.seed._session import fake, random
from scripts.seed._timeline import days_ago


NOTIFICATION_TEMPLATES = [
    (NotificationTypeEnum.OPERATION_ASSIGNMENT, NotificationSeverityEnum.INFO,    "Operation '{op_name}' assigned to you on MO-{mo_id}.", "operation"),
    (NotificationTypeEnum.BLOCKING_ALERT,       NotificationSeverityEnum.ERROR,   "Operation '{op_name}' on MO-{mo_id} is BLOCKED — quality hold active.", "operation"),
    (NotificationTypeEnum.OVERALLOCATION_WARNING, NotificationSeverityEnum.WARNING, "{wc_name} is over 95% scheduled for {date}.", "workcenter"),
    (NotificationTypeEnum.SCHEDULE_CHANGE,      NotificationSeverityEnum.INFO,    "Schedule for MO-{mo_id} shifted by 2 days.", "manufacturing_order"),
    (NotificationTypeEnum.GENERAL,              NotificationSeverityEnum.INFO,    "Weekly throughput report available.", "report"),
    (NotificationTypeEnum.GENERAL,              NotificationSeverityEnum.WARNING, "PO-{po_id} delivery overdue by {days} days.", "purchase_order"),
]


async def seed(session: AsyncSession, refs: dict) -> dict:
    users = refs["users"]
    mos = refs.get("manufacturing_orders", [])
    work_centers = list(refs.get("work_centers", {}).values())

    active_users = [u for u in users.values() if u.username != "viewer"]
    notifications: list[Notification] = []
    for user in active_users:
        per_user = random.randint(20, 40)
        for _ in range(per_user):
            tpl_type, severity, template, entity_type = random.choice(NOTIFICATION_TEMPLATES)
            mo = random.choice(mos) if mos else None
            wc = random.choice(work_centers) if work_centers else None
            msg = template.format(
                op_name=fake.bs().title(),
                mo_id=mo.id if mo else 0,
                wc_name=wc.name if wc else "Work Center",
                date=fake.date_this_year(),
                po_id=random.randint(1, 50),
                days=random.randint(1, 10),
            )
            ts = days_ago(random.randint(0, 30))
            notifications.append(Notification(
                user_id=user.id,
                message=msg,
                read=random.random() < 0.65,
                timestamp=ts,
                notification_type=tpl_type,
                related_entity_type=entity_type,
                related_entity_id=(mo.id if mo and entity_type in ("operation", "manufacturing_order") else None),
                severity=severity,
                action_url=f"/{entity_type}s/{mo.id}" if mo else None,
            ))
    session.add_all(notifications)
    await session.flush()

    print(f"  notifications: {len(notifications)} entries across {len(active_users)} users")
    return {"notifications": notifications}
