"""add_email_tracking_to_quotations

Revision ID: 4d39f0412da7
Revises: add_document_linking
Create Date: 2025-11-16 11:22:06.648359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d39f0412da7'
down_revision: Union[str, None] = 'add_document_linking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add email tracking fields to quotations table
    op.add_column('quotations', sa.Column('email_sent_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('quotations', sa.Column('email_sent_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('quotations', sa.Column('email_history', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove email tracking fields from quotations table
    op.drop_column('quotations', 'email_history')
    op.drop_column('quotations', 'email_sent_count')
    op.drop_column('quotations', 'email_sent_at')

