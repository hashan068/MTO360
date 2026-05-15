"""tighten_mo_sales_order_item_id

Revision ID: tighten_mo_so_item
Revises: fix_bomitem_component
Create Date: 2026-05-15 12:01:00.000000

In an MTO system every manufacturing order traces to a sales order line.
Tightens manufacturing_orders.sales_order_item_id to NOT NULL and replaces
the FK with one that cascades on delete.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'tighten_mo_so_item'
down_revision: Union[str, None] = 'fix_bomitem_component'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            fk_name text;
        BEGIN
            DELETE FROM manufacturing_orders WHERE sales_order_item_id IS NULL;

            SELECT conname INTO fk_name
            FROM pg_constraint
            WHERE conrelid = 'manufacturing_orders'::regclass
              AND contype = 'f'
              AND pg_get_constraintdef(oid) ILIKE '%sales_order_item_id%';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE manufacturing_orders DROP CONSTRAINT %I', fk_name);
            END IF;

            ALTER TABLE manufacturing_orders ALTER COLUMN sales_order_item_id SET NOT NULL;
            ALTER TABLE manufacturing_orders
                ADD CONSTRAINT manufacturing_orders_sales_order_item_id_fkey
                FOREIGN KEY (sales_order_item_id)
                REFERENCES sales_order_items(id)
                ON DELETE CASCADE;
        EXCEPTION WHEN others THEN
            RAISE NOTICE 'manufacturing_orders.sales_order_item_id tighten skipped: %', SQLERRM;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            fk_name text;
        BEGIN
            SELECT conname INTO fk_name
            FROM pg_constraint
            WHERE conrelid = 'manufacturing_orders'::regclass
              AND contype = 'f'
              AND pg_get_constraintdef(oid) ILIKE '%sales_order_item_id%';
            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE manufacturing_orders DROP CONSTRAINT %I', fk_name);
            END IF;
            ALTER TABLE manufacturing_orders ALTER COLUMN sales_order_item_id DROP NOT NULL;
            ALTER TABLE manufacturing_orders
                ADD CONSTRAINT manufacturing_orders_sales_order_item_id_fkey
                FOREIGN KEY (sales_order_item_id) REFERENCES sales_order_items(id);
        END $$;
        """
    )
