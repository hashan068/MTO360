"""add_procurement_models

Revision ID: 4cbd7e0af2eb
Revises: add_scheduling_indexes
Create Date: 2025-11-25 19:21:40.920867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4cbd7e0af2eb'
down_revision: Union[str, None] = 'add_scheduling_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def _create_enum_if_missing(name: str, values: tuple[str, ...]) -> None:
    quoted = ", ".join(f"'{v}'" for v in values)
    op.execute(
        f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({quoted});
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        """
    )


def upgrade() -> None:
    _create_enum_if_missing('rfqstatusenum', ('draft', 'sent', 'quotes_received', 'awarded', 'cancelled'))
    _create_enum_if_missing('quotestatusenum', ('pending', 'submitted', 'accepted', 'rejected'))
    _create_enum_if_missing('contractstatusenum', ('draft', 'active', 'expired', 'cancelled'))
    _create_enum_if_missing('abcclassificationenum', ('A', 'B', 'C'))
    _create_enum_if_missing('forecastmethodenum', ('simple_moving_average', 'weighted_moving_average', 'exponential_smoothing', 'manual'))
    _create_enum_if_missing('pricechangesourceenum', ('purchase_order', 'contract_update', 'manual_edit', 'quote'))
    
    
    # 1. Supplier Performance
    op.create_table(
        'supplier_performance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.Date(), nullable=False),
        sa.Column('on_time_delivery_rate', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('quality_rating', sa.Numeric(5, 2), nullable=False, server_default='100.00'),
        sa.Column('average_lead_time_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('price_competitiveness_score', sa.Numeric(5, 2), nullable=False, server_default='100.00'),
        sa.Column('total_spend', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        sa.Column('overall_score', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supplier_performance_supplier_period', 'supplier_performance', ['supplier_id', 'period'], unique=True)
    op.create_index('ix_supplier_performance_overall_score', 'supplier_performance', ['overall_score'])
    
    # 2. Procurement RFQ
    op.create_table(
        'procurement_rfqs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rfq_number', sa.String(50), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('required_by_date', sa.Date(), nullable=False),
        sa.Column('closing_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'sent', 'quotes_received', 'awarded', 'cancelled', name='rfqstatusenum'), nullable=False, server_default='draft'),
        sa.Column('specifications', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('awarded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['component_id'], ['components.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfq_number')
    )
    op.create_index('ix_procurement_rfqs_status', 'procurement_rfqs', ['status'])
    op.create_index('ix_procurement_rfqs_component', 'procurement_rfqs', ['component_id'])
    
    # 3. Supplier Quotes
    op.create_table(
        'supplier_quotes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rfq_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('lead_time_days', sa.Integer(), nullable=False),
        sa.Column('minimum_order_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('quote_valid_until', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'submitted', 'accepted', 'rejected', name='quotestatusenum'), nullable=False, server_default='pending'),
        sa.Column('is_awarded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('awarded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('award_justification', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['rfq_id'], ['procurement_rfqs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supplier_quotes_rfq', 'supplier_quotes', ['rfq_id'])
    op.create_index('ix_supplier_quotes_supplier', 'supplier_quotes', ['supplier_id'])
    
    # 4. Supplier Contracts
    op.create_table(
        'supplier_contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_number', sa.String(50), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('payment_terms', sa.String(50), nullable=False),
        sa.Column('volume_discounts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'expired', 'cancelled', name='contractstatusenum'), nullable=False, server_default='draft'),
        sa.Column('contract_file_url', sa.String(500), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('renewal_notice_days', sa.Integer(), nullable=False, server_default='90'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_number')
    )
    op.create_index('ix_supplier_contracts_supplier', 'supplier_contracts', ['supplier_id'])
    op.create_index('ix_supplier_contracts_status', 'supplier_contracts', ['status'])
    op.create_index('ix_supplier_contracts_end_date', 'supplier_contracts', ['end_date'])
    
    # 5. Contract Pricing
    op.create_table(
        'contract_pricing',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('minimum_order_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['supplier_contracts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['component_id'], ['components.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contract_pricing_contract', 'contract_pricing', ['contract_id'])
    op.create_index('ix_contract_pricing_component', 'contract_pricing', ['component_id'])
    
    # 6. Component Inventory Policies
    op.create_table(
        'component_inventory_policies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('reorder_point', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('safety_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('economic_order_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('abc_classification', postgresql.ENUM('A', 'B', 'C', name='abcclassificationenum'), nullable=False, server_default='C'),
        sa.Column('average_monthly_demand', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ordering_cost', sa.Numeric(10, 2), nullable=False, server_default='50.00'),
        sa.Column('holding_cost_pct', sa.Numeric(5, 2), nullable=False, server_default='25.00'),
        sa.Column('auto_pr_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('last_calculated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('component_id')
    )
    op.create_index('ix_inventory_policies_classification', 'component_inventory_policies', ['abc_classification'])
    
    # 7. Demand Forecasts
    op.create_table(
        'demand_forecasts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('forecast_month', sa.Date(), nullable=False),
        sa.Column('forecasted_demand', sa.Integer(), nullable=False),
        sa.Column('actual_demand', sa.Integer(), nullable=True),
        sa.Column('forecast_method', postgresql.ENUM('simple_moving_average', 'weighted_moving_average', 'exponential_smoothing', 'manual', name='forecastmethodenum'), nullable=False),
        sa.Column('forecast_accuracy_mape', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_demand_forecasts_component_month', 'demand_forecasts', ['component_id', 'forecast_month'], unique=True)
    
    # 8. Component Price History
    op.create_table(
        'component_price_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('price_change_source', postgresql.ENUM('purchase_order', 'contract_update', 'manual_edit', 'quote', name='pricechangesourceenum'), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('recorded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_history_component', 'component_price_history', ['component_id'])
    op.create_index('ix_price_history_effective_date', 'component_price_history', ['effective_date'])
    
    # 9. Procurement Budgets
    op.create_table(
        'procurement_budgets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('budgeted_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('actual_spend', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        sa.Column('variance', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        sa.Column('variance_pct', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_procurement_budgets_year_category', 'procurement_budgets', ['fiscal_year', 'category_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('procurement_budgets')
    op.drop_table('component_price_history')
    op.drop_table('demand_forecasts')
    op.drop_table('component_inventory_policies')
    op.drop_table('contract_pricing')
    op.drop_table('supplier_contracts')
    op.drop_table('supplier_quotes')
    op.drop_table('procurement_rfqs')
    op.drop_table('supplier_performance')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS pricechangesourceenum')
    op.execute('DROP TYPE IF EXISTS forecastmethodenum')
    op.execute('DROP TYPE IF EXISTS abcclassificationenum')
    op.execute('DROP TYPE IF EXISTS contractstatusenum')
    op.execute('DROP TYPE IF EXISTS quotestatusenum')
    op.execute('DROP TYPE IF EXISTS rfqstatusenum')
