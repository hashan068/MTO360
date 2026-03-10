"""Add performance indexes for production scheduling

Revision ID: add_scheduling_indexes
Revises: add_production_scheduling
Create Date: 2025-01-15

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'add_scheduling_indexes'
down_revision = 'add_quality_mgmt'
branch_labels = None
depends_on = None


def upgrade():
    """Create performance indexes for production scheduling"""
    
    # Critical indexes for scheduling queries
    op.create_index(
        'idx_mo_ops_wc_scheduled',
        'manufacturing_order_operations',
        ['work_center_id', 'scheduled_start', 'scheduled_end']
    )
    
    op.create_index(
        'idx_mo_ops_wc_status',
        'manufacturing_order_operations',
        ['work_center_id', 'status']
    )
    
    op.create_index(
        'idx_mo_ops_operator',
        'manufacturing_order_operations',
        ['assigned_operator_id']
    )
    
    op.create_index(
        'idx_mo_ops_completed',
        'manufacturing_order_operations',
        ['status', 'actual_end']
    )
    
    op.create_index(
        'idx_wc_schedule_date',
        'work_center_schedules',
        ['work_center_id', 'date']
    )
    
    # Analytics performance indexes
    op.create_index(
        'idx_wc_schedule_date_range',
        'work_center_schedules',
        ['date', 'work_center_id']
    )
    
    op.create_index(
        'idx_mo_ops_route',
        'manufacturing_order_operations',
        ['route_operation_id', 'status']
    )
    
    op.create_index(
        'idx_mo_completed',
        'manufacturing_orders',
        ['status', 'product_id', 'end_at']
    )
    
    # Additional useful indexes
    op.create_index(
        'idx_mo_ops_mo_id',
        'manufacturing_order_operations',
        ['manufacturing_order_id', 'sequence']
    )


def downgrade():
    """Remove performance indexes"""
    
    op.drop_index('idx_mo_ops_mo_id', 'manufacturing_order_operations')
    op.drop_index('idx_mo_completed', 'manufacturing_orders')
    op.drop_index('idx_mo_ops_route', 'manufacturing_order_operations')
    op.drop_index('idx_wc_schedule_date_range', 'work_center_schedules')
    op.drop_index('idx_wc_schedule_date', 'work_center_schedules')
    op.drop_index('idx_mo_ops_completed', 'manufacturing_order_operations')
    op.drop_index('idx_mo_ops_operator', 'manufacturing_order_operations')
    op.drop_index('idx_mo_ops_wc_status', 'manufacturing_order_operations')
    op.drop_index('idx_mo_ops_wc_scheduled', 'manufacturing_order_operations')
