"""add_production_scheduling_tables

Revision ID: add_prod_scheduling
Revises: 4d39f0412da7
Create Date: 2025-11-23 20:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision: str = 'add_prod_scheduling'
down_revision: Union[str, None] = '4d39f0412da7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create work_centers table
    op.create_table(
        'work_centers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('capacity_hours_per_day', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Create operation_routes table
    op.create_table(
        'operation_routes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('bom_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['bom_id'], ['bill_of_materials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create route_operations table
    op.create_table(
        'route_operations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('work_center_id', sa.Integer(), nullable=False),
        sa.Column('standard_time_minutes', sa.Integer(), nullable=False),
        sa.Column('setup_time_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['route_id'], ['operation_routes.id'], ),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create manufacturing_order_operations table
    op.create_table(
        'manufacturing_order_operations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=False),
        sa.Column('route_operation_id', sa.Integer(), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('work_center_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_duration_minutes', sa.Integer(), nullable=False),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'scheduled', 'in_progress', 'completed', 'blocked', 'cancelled', name='operationstatusenum'), nullable=False, server_default='pending'),
        sa.Column('assigned_operator_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('blocking_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['route_operation_id'], ['route_operations.id'], ),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.ForeignKeyConstraint(['assigned_operator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create work_center_schedules table
    op.create_table(
        'work_center_schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('work_center_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('available_capacity_minutes', sa.Integer(), nullable=False),
        sa.Column('scheduled_capacity_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('utilization_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add scheduling fields to manufacturing_orders
    op.add_column('manufacturing_orders', sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('total_scheduled_duration_minutes', sa.Integer(), nullable=True))

    # Update ManufacturingOrderStatusEnum to include 'blocked' - SQLite doesn't support ALTER TYPE
    # For SQLite, we'll need to handle this differently or document it
    # For PostgreSQL, you would use: op.execute("ALTER TYPE manufacturingorderstatusenum ADD VALUE 'blocked'")
    
    # Create indexes for performance
    op.create_index('idx_mo_operations_mo_id', 'manufacturing_order_operations', ['manufacturing_order_id'])
    op.create_index('idx_mo_operations_work_center', 'manufacturing_order_operations', ['work_center_id'])
    op.create_index('idx_mo_operations_status', 'manufacturing_order_operations', ['status'])
    op.create_index('idx_mo_operations_scheduled_start', 'manufacturing_order_operations', ['scheduled_start'])
    op.create_index('idx_work_center_schedule_date', 'work_center_schedules', ['work_center_id', 'date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_work_center_schedule_date', table_name='work_center_schedules')
    op.drop_index('idx_mo_operations_scheduled_start', table_name='manufacturing_order_operations')
    op.drop_index('idx_mo_operations_status', table_name='manufacturing_order_operations')
    op.drop_index('idx_mo_operations_work_center', table_name='manufacturing_order_operations')
    op.drop_index('idx_mo_operations_mo_id', table_name='manufacturing_order_operations')

    # Remove scheduling fields from manufacturing_orders
    op.drop_column('manufacturing_orders', 'total_scheduled_duration_minutes')
    op.drop_column('manufacturing_orders', 'scheduled_end')
    op.drop_column('manufacturing_orders', 'scheduled_start')

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('work_center_schedules')
    op.drop_table('manufacturing_order_operations')
    op.drop_table('route_operations')
    op.drop_table('operation_routes')
    op.drop_table('work_centers')
