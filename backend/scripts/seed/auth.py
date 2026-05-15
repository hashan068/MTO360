"""Auth seed: users, roles, permissions, and grants."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.auth import get_password_hash
from app.models.permissions import Permission, Role
from app.models.user import User


PERMISSIONS = [
    # Sales
    ("sales", "sales.rfq.read", "Read RFQs"),
    ("sales", "sales.rfq.write", "Create/edit RFQs"),
    ("sales", "sales.quotation.read", "Read quotations"),
    ("sales", "sales.quotation.write", "Create/edit quotations"),
    ("sales", "sales.order.read", "Read sales orders"),
    ("sales", "sales.order.write", "Create/edit sales orders"),
    ("sales", "sales.customer.read", "Read customers"),
    ("sales", "sales.customer.write", "Create/edit customers"),
    # Manufacturing
    ("manufacturing", "mfg.order.read", "Read manufacturing orders"),
    ("manufacturing", "mfg.order.write", "Create/edit manufacturing orders"),
    ("manufacturing", "mfg.operation.read", "Read operations"),
    ("manufacturing", "mfg.operation.execute", "Start/complete operations"),
    ("manufacturing", "mfg.operation.assign", "Assign operations"),
    ("manufacturing", "mfg.workcenter.read", "Read work centers"),
    ("manufacturing", "mfg.workcenter.write", "Manage work centers"),
    # Procurement
    ("procurement", "proc.po.read", "Read POs"),
    ("procurement", "proc.po.write", "Create/edit POs"),
    ("procurement", "proc.rfq.read", "Read procurement RFQs"),
    ("procurement", "proc.rfq.write", "Create/edit procurement RFQs"),
    ("procurement", "proc.supplier.read", "Read suppliers"),
    ("procurement", "proc.supplier.write", "Manage suppliers"),
    ("procurement", "proc.contract.read", "Read contracts"),
    ("procurement", "proc.contract.write", "Manage contracts"),
    # Inventory
    ("inventory", "inv.component.read", "Read components"),
    ("inventory", "inv.component.write", "Edit components"),
    # Quality
    ("quality", "qa.inspection.read", "Read inspections"),
    ("quality", "qa.inspection.perform", "Perform inspections"),
    ("quality", "qa.defect.read", "Read defects"),
    ("quality", "qa.defect.write", "Log/edit defects"),
    ("quality", "qa.ncr.read", "Read NCRs"),
    ("quality", "qa.ncr.write", "Create/edit NCRs"),
    ("quality", "qa.ncr.approve", "Approve NCRs"),
    ("quality", "qa.capa.read", "Read CAPAs"),
    ("quality", "qa.capa.write", "Create/edit CAPAs"),
    ("quality", "qa.hold.write", "Place/release holds"),
]


ROLES = {
    "admin": ("Administrator", "Full system access", "*"),
    "sales_manager": (
        "Sales Manager",
        "Owns sales pipeline",
        ["sales."],
    ),
    "sales_rep": (
        "Sales Representative",
        "Day-to-day sales",
        ["sales.rfq.", "sales.quotation.", "sales.order.read", "sales.customer."],
    ),
    "production_planner": (
        "Production Planner",
        "Schedules manufacturing",
        ["mfg.order.", "mfg.operation.read", "mfg.operation.assign", "mfg.workcenter.read", "inv.component.read"],
    ),
    "production_manager": (
        "Production Manager",
        "Owns the shop floor",
        ["mfg.", "inv.component.read", "qa.inspection.read", "qa.defect.read"],
    ),
    "shop_floor_operator": (
        "Shop Floor Operator",
        "Executes assigned operations",
        ["mfg.operation.read", "mfg.operation.execute", "qa.defect.write"],
    ),
    "quality_engineer": (
        "Quality Engineer",
        "Owns quality processes",
        ["qa.", "mfg.order.read", "mfg.operation.read"],
    ),
    "procurement_manager": (
        "Procurement Manager",
        "Owns supplier relations",
        ["proc.", "inv.component."],
    ),
    "viewer": ("Viewer", "Read-only", [".read"]),
}


USERS = [
    ("admin", "admin@mto360.local", "admin123", True, ["admin"]),
    ("sales_mgr", "sales.mgr@mto360.local", "demo123", False, ["sales_manager"]),
    ("sales_rep_1", "sales1@mto360.local", "demo123", False, ["sales_rep"]),
    ("sales_rep_2", "sales2@mto360.local", "demo123", False, ["sales_rep"]),
    ("planner", "planner@mto360.local", "demo123", False, ["production_planner"]),
    ("ops_mgr", "ops.mgr@mto360.local", "demo123", False, ["production_manager"]),
    ("operator_1", "operator1@mto360.local", "demo123", False, ["shop_floor_operator"]),
    ("operator_2", "operator2@mto360.local", "demo123", False, ["shop_floor_operator"]),
    ("qa_eng_1", "qa1@mto360.local", "demo123", False, ["quality_engineer"]),
    ("qa_eng_2", "qa2@mto360.local", "demo123", False, ["quality_engineer"]),
    ("proc_mgr", "proc.mgr@mto360.local", "demo123", False, ["procurement_manager"]),
    ("viewer", "viewer@mto360.local", "demo123", False, ["viewer"]),
]


def _matches(code: str, patterns: list[str] | str) -> bool:
    if patterns == "*":
        return True
    for pat in patterns:
        if pat.endswith(".") and code.startswith(pat):
            return True
        if pat.startswith(".") and code.endswith(pat):
            return True
        if pat == code:
            return True
    return False


async def seed(session: AsyncSession, refs: dict) -> dict:
    permissions: dict[str, Permission] = {}
    for module, code, name in PERMISSIONS:
        perm = Permission(module=module, code=code, name=name)
        session.add(perm)
        permissions[code] = perm
    await session.flush()

    roles: dict[str, Role] = {}
    for key, (name, desc, perm_patterns) in ROLES.items():
        role = Role(name=name, description=desc)
        for code, perm in permissions.items():
            if _matches(code, perm_patterns):
                role.permissions.append(perm)
        session.add(role)
        roles[key] = role
    await session.flush()

    users: dict[str, User] = {}
    for username, email, password, is_super, role_keys in USERS:
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            is_active=True,
            is_superuser=is_super,
            is_staff=is_super,
        )
        for rk in role_keys:
            user.roles.append(roles[rk])
        session.add(user)
        users[username] = user
    await session.flush()

    print(f"  auth: {len(permissions)} permissions, {len(roles)} roles, {len(users)} users")
    return {"users": users, "roles": roles, "permissions": permissions}
