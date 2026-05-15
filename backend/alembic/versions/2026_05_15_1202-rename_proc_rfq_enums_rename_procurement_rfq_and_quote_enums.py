"""rename_procurement_rfq_and_quote_enums

Revision ID: rename_proc_rfq_enums
Revises: tighten_mo_so_item
Create Date: 2026-05-15 12:02:00.000000

Both app.models.sales.RFQStatusEnum and app.models.procurement.RFQStatusEnum
were SQLAlchemy enum classes with the same Python name, so SQLAlchemy was
emitting both as the same Postgres type `rfqstatusenum` even though their
value sets differ. We rename the procurement Python classes and back them
with distinctly-named Postgres types (procurement_rfq_status_enum,
supplier_quote_status_enum).
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'rename_proc_rfq_enums'
down_revision: Union[str, None] = 'tighten_mo_so_item'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE procurement_rfq_status_enum AS ENUM ('draft', 'sent', 'quotes_received', 'awarded', 'cancelled');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE supplier_quote_status_enum AS ENUM ('pending', 'submitted', 'accepted', 'rejected');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        """
    )

    op.execute(
        "ALTER TABLE procurement_rfqs "
        "ALTER COLUMN status TYPE procurement_rfq_status_enum "
        "USING status::text::procurement_rfq_status_enum"
    )
    op.execute(
        "ALTER TABLE supplier_quotes "
        "ALTER COLUMN status TYPE supplier_quote_status_enum "
        "USING status::text::supplier_quote_status_enum"
    )

    # Split quality.PriorityEnum off the shared `priorityenum` Postgres type
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE quality_priority_enum AS ENUM ('URGENT', 'HIGH', 'NORMAL', 'LOW');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        "ALTER TABLE non_conformance_reports "
        "ALTER COLUMN priority TYPE quality_priority_enum "
        "USING priority::text::quality_priority_enum"
    )
    op.execute(
        "ALTER TABLE corrective_actions "
        "ALTER COLUMN priority TYPE quality_priority_enum "
        "USING priority::text::quality_priority_enum"
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE rfqstatusenum AS ENUM ('draft', 'sent', 'quotes_received', 'awarded', 'cancelled');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE quotestatusenum AS ENUM ('pending', 'submitted', 'accepted', 'rejected');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute("ALTER TABLE procurement_rfqs ALTER COLUMN status TYPE rfqstatusenum USING status::text::rfqstatusenum")
    op.execute("ALTER TABLE supplier_quotes ALTER COLUMN status TYPE quotestatusenum USING status::text::quotestatusenum")
    op.execute("DROP TYPE IF EXISTS procurement_rfq_status_enum")
    op.execute("DROP TYPE IF EXISTS supplier_quote_status_enum")
