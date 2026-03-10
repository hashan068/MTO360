"""add_quality_management_system

Revision ID: add_quality_mgmt
Revises: update_so_status
Create Date: 2025-11-24 21:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision: str = 'add_quality_mgmt'
down_revision: Union[str, None] = 'update_so_status_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create inspection_points table
    op.create_table(
        'inspection_points',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('route_operation_id', sa.Integer(), nullable=True),
        sa.Column('inspection_type', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('checklist_items', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['route_operation_id'], ['route_operations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create inspection_results table
    op.create_table(
        'inspection_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inspection_point_id', sa.Integer(), nullable=False),
        sa.Column('mo_operation_id', sa.Integer(), nullable=True),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=True),
        sa.Column('component_id', sa.Integer(), nullable=True),
        sa.Column('inspector_id', sa.Integer(), nullable=False),
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('result', sa.String(length=20), nullable=False),
        sa.Column('checklist_results', sa.JSON(), nullable=True),
        sa.Column('measurements', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('photo_urls', sa.JSON(), nullable=True),
        sa.Column('document_urls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inspection_point_id'], ['inspection_points.id'], ),
        sa.ForeignKeyConstraint(['mo_operation_id'], ['manufacturing_order_operations.id'], ),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create defects table
    op.create_table(
        'defects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('defect_number', sa.String(length=50), nullable=False),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=True),
        sa.Column('mo_operation_id', sa.Integer(), nullable=True),
        sa.Column('inspection_result_id', sa.Integer(), nullable=True),
        sa.Column('component_id', sa.Integer(), nullable=True),
        sa.Column('sales_order_id', sa.Integer(), nullable=True),
        sa.Column('defect_type', sa.String(length=20), nullable=False),
        sa.Column('defect_category', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('quantity_affected', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('reported_by_id', sa.Integer(), nullable=False),
        sa.Column('responsible_party', sa.String(length=20), nullable=False),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
        sa.Column('photo_urls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['mo_operation_id'], ['manufacturing_order_operations.id'], ),
        sa.ForeignKeyConstraint(['inspection_result_id'], ['inspection_results.id'], ),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_orders.id'], ),
        sa.ForeignKeyConstraint(['reported_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('defect_number')
    )
    
    # Create non_conformance_reports table
    op.create_table(
        'non_conformance_reports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ncr_number', sa.String(length=50), nullable=False),
        sa.Column('defect_id', sa.Integer(), nullable=True),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('root_cause_category', sa.String(length=100), nullable=True),
        sa.Column('containment_actions', sa.Text(), nullable=True),
        sa.Column('disposition', sa.String(length=30), nullable=True),
        sa.Column('disposition_justification', sa.Text(), nullable=True),
        sa.Column('quantity_affected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rework_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('scrap_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('closed_by_id', sa.Integer(), nullable=True),
        sa.Column('closed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], ),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ncr_number')
    )
    
    # Create rework_operations table
    op.create_table(
        'rework_operations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ncr_id', sa.Integer(), nullable=False),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=False),
        sa.Column('work_center_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_duration_minutes', sa.Integer(), nullable=False),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('assigned_operator_id', sa.Integer(), nullable=True),
        sa.Column('rework_description', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('labor_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('material_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('re_inspection_result_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ncr_id'], ['non_conformance_reports.id'], ),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ),
        sa.ForeignKeyConstraint(['assigned_operator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['re_inspection_result_id'], ['inspection_results.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create corrective_actions table (CAPA)
    op.create_table(
        'corrective_actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('capa_number', sa.String(length=50), nullable=False),
        sa.Column('ncr_id', sa.Integer(), nullable=True),
        sa.Column('defect_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('problem_statement', sa.Text(), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=False),
        sa.Column('root_cause_method', sa.String(length=50), nullable=True),
        sa.Column('root_cause_analysis', sa.JSON(), nullable=True),
        sa.Column('corrective_actions', sa.JSON(), nullable=True),
        sa.Column('preventive_actions', sa.JSON(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('effectiveness_verification', sa.Text(), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_id', sa.Integer(), nullable=True),
        sa.Column('closed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ncr_id'], ['non_conformance_reports.id'], ),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['verified_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('capa_number')
    )
    
    # Create quality_holds table
    op.create_table(
        'quality_holds',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hold_number', sa.String(length=50), nullable=False),
        sa.Column('ncr_id', sa.Integer(), nullable=False),
        sa.Column('hold_type', sa.String(length=30), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=True),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=True),
        sa.Column('sales_order_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('quantity_held', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('placed_by_id', sa.Integer(), nullable=False),
        sa.Column('placed_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('released_by_id', sa.Integer(), nullable=True),
        sa.Column('released_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('release_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ncr_id'], ['non_conformance_reports.id'], ),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_orders.id'], ),
        sa.ForeignKeyConstraint(['placed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['released_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hold_number')
    )
    
    # Add quality fields to manufacturing_orders
    op.add_column('manufacturing_orders', sa.Column('quality_status', sa.String(length=50), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('final_inspection_result_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_manufacturing_orders_final_inspection_result',
        'manufacturing_orders', 'inspection_results',
        ['final_inspection_result_id'], ['id']
    )
    
    # Add quality fields to manufacturing_order_operations
    op.add_column('manufacturing_order_operations', sa.Column('inspection_status', sa.String(length=50), nullable=True))
    op.add_column('manufacturing_order_operations', sa.Column('quality_hold', sa.Boolean(), nullable=False, server_default='0'))
    
    # Create indexes for query performance
    op.create_index('idx_inspection_results_mo_operation', 'inspection_results', ['mo_operation_id'])
    op.create_index('idx_inspection_results_inspector', 'inspection_results', ['inspector_id'])
    op.create_index('idx_inspection_results_date', 'inspection_results', ['inspection_date'])
    op.create_index('idx_defects_mo', 'defects', ['manufacturing_order_id'])
    op.create_index('idx_defects_type_severity', 'defects', ['defect_type', 'severity'])
    op.create_index('idx_defects_date', 'defects', ['created_at'])
    op.create_index('idx_ncrs_status', 'non_conformance_reports', ['status'])
    op.create_index('idx_ncrs_priority', 'non_conformance_reports', ['priority'])
    op.create_index('idx_capas_status', 'corrective_actions', ['status'])
    op.create_index('idx_quality_holds_status', 'quality_holds', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_quality_holds_status', table_name='quality_holds')
    op.drop_index('idx_capas_status', table_name='corrective_actions')
    op.drop_index('idx_ncrs_priority', table_name='non_conformance_reports')
    op.drop_index('idx_ncrs_status', table_name='non_conformance_reports')
    op.drop_index('idx_defects_date', table_name='defects')
    op.drop_index('idx_defects_type_severity', table_name='defects')
    op.drop_index('idx_defects_mo', table_name='defects')
    op.drop_index('idx_inspection_results_date', table_name='inspection_results')
    op.drop_index('idx_inspection_results_inspector', table_name='inspection_results')
    op.drop_index('idx_inspection_results_mo_operation', table_name='inspection_results')
    
    # Remove quality fields from manufacturing_order_operations
    op.drop_column('manufacturing_order_operations', 'quality_hold')
    op.drop_column('manufacturing_order_operations', 'inspection_status')
    
    # Remove quality fields from manufacturing_orders
    op.drop_constraint('fk_manufacturing_orders_final_inspection_result', 'manufacturing_orders', type_='foreignkey')
    op.drop_column('manufacturing_orders', 'final_inspection_result_id')
    op.drop_column('manufacturing_orders', 'quality_status')
    
    # Drop tables in reverse order of creation
    op.drop_table('quality_holds')
    op.drop_table('corrective_actions')
    op.drop_table('rework_operations')
    op.drop_table('non_conformance_reports')
    op.drop_table('defects')
    op.drop_table('inspection_results')
    op.drop_table('inspection_points')
