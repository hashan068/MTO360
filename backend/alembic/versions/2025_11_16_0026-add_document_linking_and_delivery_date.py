"""Add document linking and delivery date

Revision ID: add_document_linking
Revises: 
Create Date: 2025-11-16 00:26:00.000000

This migration adds:
- rfq_id foreign key to quotations table for RFQ to Quotation linking
- quotation_id foreign key to sales_orders table for Quotation to Sales Order linking
- delivery_date column to sales_orders table
- Database indexes for performance optimization on foreign keys and status fields
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_document_linking'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade database schema:
    - Add rfq_id to quotations table
    - Add quotation_id to sales_orders table
    - Add delivery_date to sales_orders table
    - Create foreign key constraints
    - Create indexes for performance optimization
    """
    
    # Add rfq_id column to quotations table
    op.add_column('quotations', sa.Column('rfq_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for quotations.rfq_id
    op.create_foreign_key(
        'fk_quotations_rfq_id',
        'quotations',
        'rfqs',
        ['rfq_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index on quotations.rfq_id for faster lookups
    op.create_index('ix_quotations_rfq_id', 'quotations', ['rfq_id'])
    
    # Add quotation_id column to sales_orders table
    op.add_column('sales_orders', sa.Column('quotation_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for sales_orders.quotation_id
    op.create_foreign_key(
        'fk_sales_orders_quotation_id',
        'sales_orders',
        'quotations',
        ['quotation_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index on sales_orders.quotation_id for faster lookups
    op.create_index('ix_sales_orders_quotation_id', 'sales_orders', ['quotation_id'])
    
    # Add delivery_date column to sales_orders table
    op.add_column('sales_orders', sa.Column('delivery_date', sa.DateTime(timezone=True), nullable=True))
    
    # Create composite indexes for common query patterns
    # Index for filtering quotations by status and creation date
    op.create_index('ix_quotations_status_created_at', 'quotations', ['status', 'created_at'])
    
    # Index for filtering sales orders by status and creation date
    op.create_index('ix_sales_orders_status_created_at', 'sales_orders', ['status', 'created_at'])
    
    # Index for filtering RFQs by status and creation date
    op.create_index('ix_rfqs_status_created_at', 'rfqs', ['status', 'created_at'])


def downgrade() -> None:
    """
    Downgrade database schema:
    - Remove all indexes
    - Remove foreign key constraints
    - Remove added columns
    """
    
    # Drop indexes
    op.drop_index('ix_rfqs_status_created_at', table_name='rfqs')
    op.drop_index('ix_sales_orders_status_created_at', table_name='sales_orders')
    op.drop_index('ix_quotations_status_created_at', table_name='quotations')
    op.drop_index('ix_sales_orders_quotation_id', table_name='sales_orders')
    op.drop_index('ix_quotations_rfq_id', table_name='quotations')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_sales_orders_quotation_id', 'sales_orders', type_='foreignkey')
    op.drop_constraint('fk_quotations_rfq_id', 'quotations', type_='foreignkey')
    
    # Drop columns
    op.drop_column('sales_orders', 'delivery_date')
    op.drop_column('sales_orders', 'quotation_id')
    op.drop_column('quotations', 'rfq_id')
