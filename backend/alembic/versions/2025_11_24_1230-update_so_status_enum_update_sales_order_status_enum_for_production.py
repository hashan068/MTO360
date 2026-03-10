"""update_sales_order_status_enum_for_production

Revision ID: update_so_status_enum
Revises: add_permissions_roles
Create Date: 2025-11-24 12:30:00.000000

This migration updates the SalesOrderStatusEnum to add production-related statuses
and fix naming inconsistencies for better integration with manufacturing module.

Changes:
- Add PRODUCTION_SCHEDULED status
- Fix IN_PRODUCTION typo (was "in_Production")
- Add PRODUCTION_DELAYED status
- Rename READY_FOR_DELIVERY to READY_TO_SHIP
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_so_status_enum'
down_revision: Union[str, None] = 'add_permissions_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Update SalesOrderStatusEnum to add production-related statuses.
    
    Note: For PostgreSQL, we need to use ALTER TYPE statements.
    For SQLite (development), enum changes are handled differently.
    """
    # Check if we're using PostgreSQL
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        # PostgreSQL: Use ALTER TYPE to add new enum values
        
        # Add new status: PRODUCTION_SCHEDULED
        op.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'production_scheduled' 
                    AND enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'salesorderstatusenum'
                    )
                ) THEN
                    ALTER TYPE salesorderstatusenum ADD VALUE 'production_scheduled';
                END IF;
            END $$;
        """)
        
        # Add new status: PRODUCTION_DELAYED
        op.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'production_delayed' 
                    AND enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'salesorderstatusenum'
                    )
                ) THEN
                    ALTER TYPE salesorderstatusenum ADD VALUE 'production_delayed';
                END IF;
            END $$;
        """)
        
        # Add new status: READY_TO_SHIP (replacement for READY_FOR_DELIVERY)
        op.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'ready_to_ship' 
                    AND enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'salesorderstatusenum'
                    )
                ) THEN
                    ALTER TYPE salesorderstatusenum ADD VALUE 'ready_to_ship';
                END IF;
            END $$;
        """)
        
        # Update existing data: Fix IN_PRODUCTION typo
        op.execute("""
            UPDATE sales_orders 
            SET status = 'in_production' 
            WHERE status = 'in_Production';
        """)
        
        # Update existing data: Migrate READY_FOR_DELIVERY to READY_TO_SHIP
        op.execute("""
            UPDATE sales_orders 
            SET status = 'ready_to_ship' 
            WHERE status = 'Ready_for_delivery';
        """)
        
    # For SQLite and other databases, the enum is just a check constraint
    # The model changes will handle this automatically


def downgrade() -> None:
    """
    Revert SalesOrderStatusEnum changes.
    
    Note: PostgreSQL doesn't support removing enum values easily.
    We'll update the data to use old values but keep the new enum values.
    """
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        # Migrate data back to old values
        
        # Change ready_to_ship back to Ready_for_delivery
        op.execute("""
            UPDATE sales_orders 
            SET status = 'Ready_for_delivery' 
            WHERE status = 'ready_to_ship';
        """)
        
        # Change in_production back to in_Production
        op.execute("""
            UPDATE sales_orders 
            SET status = 'in_Production' 
            WHERE status = 'in_production';
        """)
        
        # Change new statuses to closest equivalent
        op.execute("""
            UPDATE sales_orders 
            SET status = 'confirmed' 
            WHERE status = 'production_scheduled';
        """)
        
        op.execute("""
            UPDATE sales_orders 
            SET status = 'pending' 
            WHERE status = 'production_delayed';
        """)
        
        # Note: We can't easily remove enum values in PostgreSQL
        # The new values will remain in the enum type but won't be used
