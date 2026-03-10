"""
Quality Management Permissions Seed Data
Defines all quality-specific permissions and roles for RBAC
"""
from sqlalchemy.orm import Session
from app.models.permissions import Permission, Role


# Quality Permission Definitions
QUALITY_PERMISSIONS = [
    # Inspection Permissions
    {
        "name": "Create Inspection Point",
        "code": "quality.inspection_point.create",
        "description": "Create new inspection points",
        "module": "quality"
    },
    {
        "name": "View Inspection Points",
        "code": "quality.inspection_point.read",
        "description": "View inspection point definitions",
        "module": "quality"
    },
    {
        "name": "Update Inspection Point",
        "code": "quality.inspection_point.update",
        "description": "Modify inspection point definitions",
        "module": "quality"
    },
    {
        "name": "Delete Inspection Point",
        "code": "quality.inspection_point.delete",
        "description": "Delete inspection point definitions",
        "module": "quality"
    },
    {
        "name": "Perform Inspection",
        "code": "quality.inspection.perform",
        "description": "Record inspection results",
        "module": "quality"
    },
    {
        "name": "View Inspections",
        "code": "quality.inspection.read",
        "description": "View inspection results",
        "module": "quality"
    },
    {
        "name": "Update Inspection",
        "code": "quality.inspection.update",
        "description": "Modify inspection results",
        "module": "quality"
    },
    
    # Defect Permissions
    {
        "name": "Create Defect",
        "code": "quality.defect.create",
        "description": "Report new defects",
        "module": "quality"
    },
    {
        "name": "View Defects",
        "code": "quality.defect.read",
        "description": "View defect records",
        "module": "quality"
    },
    {
        "name": "Update Defect",
        "code": "quality.defect.update",
        "description": "Modify defect records",
        "module": "quality"
    },
    {
        "name": "Close Defect",
        "code": "quality.defect.close",
        "description": "Close defect records",
        "module": "quality"
    },
    
    # NCR Permissions
    {
        "name": "Create NCR",
        "code": "quality.ncr.create",
        "description": "Create non-conformance reports",
        "module": "quality"
    },
    {
        "name": "View NCRs",
        "code": "quality.ncr.read",
        "description": "View non-conformance reports",
        "module": "quality"
    },
    {
        "name": "Update NCR",
        "code": "quality.ncr.update",
        "description": "Modify non-conformance reports",
        "module": "quality"
    },
    {
        "name": "Approve NCR",
        "code": "quality.ncr.approve",
        "description": "Approve NCR dispositions",
        "module": "quality"
    },
    {
        "name": "Close NCR",
        "code": "quality.ncr.close",
        "description": "Close non-conformance reports",
        "module": "quality"
    },
    
    # Rework Permissions
    {
        "name": "Create Rework",
        "code": "quality.rework.create",
        "description": "Create rework operations",
        "module": "quality"
    },
    {
        "name": "View Rework",
        "code": "quality.rework.read",
        "description": "View rework operations",
        "module": "quality"
    },
    {
        "name": "Perform Rework",
        "code": "quality.rework.perform",
        "description": "Execute rework operations",
        "module": "quality"
    },
    
    # CAPA Permissions
    {
        "name": "Create CAPA",
        "code": "quality.capa.create",
        "description": "Create corrective/preventive actions",
        "module": "quality"
    },
    {
        "name": "View CAPAs",
        "code": "quality.capa.read",
        "description": "View corrective/preventive actions",
        "module": "quality"
    },
    {
        "name": "Update CAPA",
        "code": "quality.capa.update",
        "description": "Modify CAPA records and actions",
        "module": "quality"
    },
    {
        "name": "Verify CAPA",
        "code": "quality.capa.verify",
        "description": "Verify CAPA effectiveness",
        "module": "quality"
    },
    {
        "name": "Close CAPA",
        "code": "quality.capa.close",
        "description": "Close CAPA records",
        "module": "quality"
    },
    
    # Quality Hold Permissions
    {
        "name": "Place Quality Hold",
        "code": "quality.hold.create",
        "description": "Place quality holds on inventory/orders",
        "module": "quality"
    },
    {
        "name": "View Quality Holds",
        "code": "quality.hold.read",
        "description": "View quality hold records",
        "module": "quality"
    },
    {
        "name": "Release Quality Hold",
        "code": "quality.hold.release",
        "description": "Release quality holds",
        "module": "quality"
    },
    
    # Analytics Permissions
    {
        "name": "View Quality Analytics",
        "code": "quality.analytics.read",
        "description": "View quality metrics and reports",
        "module": "quality"
    },
]


# Quality Role Definitions
QUALITY_ROLES = [
    {
        "name": "Quality Inspector",
        "description": "Shop floor quality inspector - performs inspections and reports defects",
        "permissions": [
            "quality.inspection.perform",
            "quality.inspection.read",
            "quality.defect.create",
            "quality.defect.read",
            "quality.rework.read",
        ]
    },
    {
        "name": "Quality Engineer",
        "description": "Quality engineer - manages NCRs, CAPAs, and quality processes",
        "permissions": [
            "quality.inspection_point.create",
            "quality.inspection_point.read",
            "quality.inspection_point.update",
            "quality.inspection.read",
            "quality.defect.read",
            "quality.defect.update",
            "quality.defect.close",
            "quality.ncr.create",
            "quality.ncr.read",
            "quality.ncr.update",
            "quality.ncr.close",
            "quality.capa.create",
            "quality.capa.read",
            "quality.capa.update",
            "quality.capa.close",
            "quality.rework.create",
            "quality.rework.read",
            "quality.hold.create",
            "quality.hold.read",
        ]
    },
    {
        "name": "Quality Manager",
        "description": "Quality manager - full quality system access with approval authority",
        "permissions": [
            # All inspection permissions
            "quality.inspection_point.create",
            "quality.inspection_point.read",
            "quality.inspection_point.update",
            "quality.inspection_point.delete",
            "quality.inspection.perform",
            "quality.inspection.read",
            "quality.inspection.update",
            # All defect permissions
            "quality.defect.create",
            "quality.defect.read",
            "quality.defect.update",
            "quality.defect.close",
            # All NCR permissions
            "quality.ncr.create",
            "quality.ncr.read",
            "quality.ncr.update",
            "quality.ncr.approve",
            "quality.ncr.close",
            # All CAPA permissions
            "quality.capa.create",
            "quality.capa.read",
            "quality.capa.update",
            "quality.capa.verify",
            "quality.capa.close",
            # All rework permissions
            "quality.rework.create",
            "quality.rework.read",
            "quality.rework.perform",
            # All hold permissions
            "quality.hold.create",
            "quality.hold.read",
            "quality.hold.release",
            # Analytics
            "quality.analytics.read",
        ]
    },
]


def seed_quality_permissions(db: Session) -> dict:
    """
    Seed quality permissions and roles into database
    
    Args:
        db: Database session
        
    Returns:
        Dict with counts of created permissions and roles
    """
    created_permissions = 0
    created_roles = 0
    
    # Create permissions
    permission_map = {}
    for perm_data in QUALITY_PERMISSIONS:
        # Check if permission already exists
        existing = db.query(Permission).filter(
            Permission.code == perm_data["code"]
        ).first()
        
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            db.flush()
            permission_map[perm_data["code"]] = permission
            created_permissions += 1
        else:
            permission_map[perm_data["code"]] = existing
    
    db.commit()
    
    # Create roles
    for role_data in QUALITY_ROLES:
        # Check if role already exists
        existing_role = db.query(Role).filter(
            Role.name == role_data["name"]
        ).first()
        
        if not existing_role:
            # Create role
            role = Role(
                name=role_data["name"],
                description=role_data["description"]
            )
            
            # Add permissions to role
            for perm_code in role_data["permissions"]:
                if perm_code in permission_map:
                    role.permissions.append(permission_map[perm_code])
            
            db.add(role)
            created_roles += 1
        else:
            # Update existing role permissions
            existing_role.permissions.clear()
            for perm_code in role_data["permissions"]:
                if perm_code in permission_map:
                    existing_role.permissions.append(permission_map[perm_code])
    
    db.commit()
    
    return {
        "permissions_created": created_permissions,
        "roles_created": created_roles,
        "total_permissions": len(QUALITY_PERMISSIONS),
        "total_roles": len(QUALITY_ROLES)
    }


if __name__ == "__main__":
    """Run seed script directly"""
    import sys
    import os
    
    # Add backend directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config.settings import settings
    
    # Create sync engine from async URL
    # Replace postgresql+asyncpg with postgresql
    sync_url = settings.get_database_url().replace("postgresql+asyncpg", "postgresql")
    
    engine = create_engine(sync_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        result = seed_quality_permissions(db)
        print("✅ Quality permissions seeded successfully:")
        print(f"   - Created {result['permissions_created']}/{result['total_permissions']} permissions")
        print(f"   - Created {result['roles_created']}/{result['total_roles']} roles")
    except Exception as e:
        print(f"❌ Error seeding permissions: {e}")
        db.rollback()
    finally:
        db.close()
