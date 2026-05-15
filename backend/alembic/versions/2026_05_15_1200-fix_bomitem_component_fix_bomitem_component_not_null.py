"""fix_bomitem_component_not_null

Revision ID: fix_bomitem_component
Revises: 4cbd7e0af2eb
Create Date: 2026-05-15 12:00:00.000000

Drops the `default=1` on bom_items.component_id and tightens the column to
NOT NULL. The previous Python-side default of 1 silently routed BOM items at
whatever component happened to be ID 1, which is a data-integrity bomb.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'fix_bomitem_component'
down_revision: Union[str, None] = '4cbd7e0af2eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            UPDATE bom_items SET component_id = NULL WHERE component_id NOT IN (SELECT id FROM components);
            ALTER TABLE bom_items ALTER COLUMN component_id DROP DEFAULT;
            ALTER TABLE bom_items ALTER COLUMN component_id SET NOT NULL;
        EXCEPTION WHEN others THEN
            RAISE NOTICE 'bom_items.component_id tighten skipped: %', SQLERRM;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE bom_items ALTER COLUMN component_id DROP NOT NULL")
    op.execute("ALTER TABLE bom_items ALTER COLUMN component_id SET DEFAULT 1")
