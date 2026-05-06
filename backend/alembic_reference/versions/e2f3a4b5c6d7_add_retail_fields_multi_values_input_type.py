"""add_retail_fields_multi_values_input_type

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-05-06 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to retail table
    op.add_column('retail', sa.Column('advertising_category', sa.Text(), nullable=True))
    op.add_column('retail', sa.Column('is_seasonal', sa.Boolean(), nullable=True))
    op.add_column('retail', sa.Column('format', sa.Text(), nullable=True))
    op.add_column('retail', sa.Column('days_monitored_est', sa.Integer(), nullable=True))
    op.add_column('retail', sa.Column('group_id', sa.Text(), nullable=True))

    # Create retail_multi_values table
    op.create_table(
        'retail_multi_values',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('picture_id', sa.UUID(), nullable=False),
        sa.Column('field_name', sa.Text(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Add input_type to process_attributes
    op.add_column(
        'process_attributes',
        sa.Column('input_type', sa.Text(), nullable=False, server_default='text'),
    )


def downgrade() -> None:
    op.drop_column('process_attributes', 'input_type')
    op.drop_table('retail_multi_values')
    op.drop_column('retail', 'group_id')
    op.drop_column('retail', 'days_monitored_est')
    op.drop_column('retail', 'format')
    op.drop_column('retail', 'is_seasonal')
    op.drop_column('retail', 'advertising_category')
