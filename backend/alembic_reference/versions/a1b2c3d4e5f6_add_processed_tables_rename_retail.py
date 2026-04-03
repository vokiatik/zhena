"""add_processed_tables_rename_retail

Revision ID: a1b2c3d4e5f6
Revises: 8e069dfe2de2
Create Date: 2026-04-02 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8e069dfe2de2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables
    op.rename_table('retail_upload_rows', 'retail')
    op.rename_table('retail_upload_rows_additional', 'retail_process_additional')

    # Add process_id to retail
    op.add_column('retail', sa.Column('process_id', sa.UUID(), nullable=True))

    # Add table_name to process_types
    op.add_column('process_types', sa.Column('table_name', sa.Text(), nullable=True))

    # Add total_items and parent_process_id to processes
    op.add_column('processes', sa.Column('total_items', sa.Integer(), nullable=True))
    op.add_column('processes', sa.Column('parent_process_id', sa.UUID(), nullable=True))

    # Create retail_processed
    op.create_table('retail_processed',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('retailer_clean', sa.Text(), nullable=True),
        sa.Column('advertiser_producer', sa.Text(), nullable=True),
        sa.Column('brands_list', sa.Text(), nullable=True),
        sa.Column('brands_list_clean', sa.Text(), nullable=True),
        sa.Column('ferrero_category', sa.Text(), nullable=True),
        sa.Column('ferrero_category_range', sa.Text(), nullable=True),
        sa.Column('ferrero_category_multibrand', sa.Text(), nullable=True),
        sa.Column('first_screen_date', sa.Date(), nullable=True),
        sa.Column('last_screen_date', sa.Date(), nullable=True),
        sa.Column('advertisement_id', sa.Text(), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('process_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create analyst_processed
    op.create_table('analyst_processed',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('format', sa.Text(), nullable=True),
        sa.Column('weekly_price', sa.Text(), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('process_id', sa.UUID(), nullable=False),
        sa.Column('retail_processed_id', sa.UUID(), nullable=False),
        sa.Column('link', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('analyst_processed')
    op.drop_table('retail_processed')
    op.drop_column('processes', 'parent_process_id')
    op.drop_column('processes', 'total_items')
    op.drop_column('process_types', 'table_name')
    op.drop_column('retail', 'process_id')
    op.rename_table('retail_process_additional', 'retail_upload_rows_additional')
    op.rename_table('retail', 'retail_upload_rows')
