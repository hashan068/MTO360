"""
Permission seeding data
"""

# Define all production-related permissions
PRODUCTION_PERMISSIONS = [
    {
        "name": "View Production Schedule",
        "code": "production.schedule.view",
        "description": "View production schedules and operations",
        "module": "production"
    },
    {
        "name": "Create Production Schedule",
        "code": "production.schedule.create",
        "description": "Create new production schedules and auto-schedule manufacturing orders",
        "module": "production"
    },
    {
        "name": "Update Production Schedule",
        "code": "production.schedule.update",
        "description": "Modify existing production schedules and reschedule operations",
        "module": "production"
    },
    {
        "name": "Delete Production Schedule",
        "code": "production.schedule.delete",
        "description": "Delete production schedules",
        "module": "production"
    },
    {
        "name": "Assign Operations",
        "code": "production.operation.assign",
        "description": "Assign operations to operators",
        "module": "production"
    },
    {
        "name": "Start Operations",
        "code": "production.operation.start",
        "description": "Start manufacturing order operations",
        "module": "production"
    },
    {
        "name": "Complete Operations",
        "code": "production.operation.complete",
        "description": "Mark operations as completed",
        "module": "production"
    },
    {
        "name": "Block Operations",
        "code": "production.operation.block",
        "description": "Block operations and provide blocking reasons",
        "module": "production"
    },
    {
        "name": "Manage Work Centers",
        "code": "production.workcenter.manage",
        "description": "Create, update, and delete work centers",
        "module": "production"
    },
    {
        "name": "View Manufacturing Orders",
        "code": "production.mo.view",
        "description": "View manufacturing orders",
        "module": "production"
    },
    {
        "name": "Create Manufacturing Orders",
        "code": "production.mo.create",
        "description": "Create new manufacturing orders",
        "module": "production"
    },
    {
        "name": "Update Manufacturing Orders",
        "code": "production.mo.update",
        "description": "Update manufacturing order details",
        "module": "production"
    },
]

# Define default roles and their permission mappings
DEFAULT_ROLES = [
    {
        "name": "Production Manager",
        "description": "Full access to all production operations and scheduling",
        "permissions": [
            "production.schedule.view",
            "production.schedule.create",
            "production.schedule.update",
            "production.schedule.delete",
            "production.operation.assign",
            "production.operation.start",
            "production.operation.complete",
            "production.operation.block",
            "production.workcenter.manage",
            "production.mo.view",
            "production.mo.create",
            "production.mo.update",
        ]
    },
    {
        "name": "Production Planner",
        "description": "Can schedule production and assign operations but cannot manage work centers",
        "permissions": [
            "production.schedule.view",
            "production.schedule.create",
            "production.schedule.update",
            "production.operation.assign",
            "production.mo.view",
            "production.mo.create",
            "production.mo.update",
        ]
    },
    {
        "name": "Shop Floor Operator",
        "description": "Can view schedules and manage their assigned operations",
        "permissions": [
            "production.schedule.view",
            "production.operation.start",
            "production.operation.complete",
            "production.operation.block",
            "production.mo.view",
        ]
    },
    {
        "name": "Production Viewer",
        "description": "Read-only access to production information",
        "permissions": [
            "production.schedule.view",
            "production.mo.view",
        ]
    },
]
