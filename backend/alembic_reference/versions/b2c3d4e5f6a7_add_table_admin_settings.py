"""add_table_admin_settings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'table_admin_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('table_name', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('visible', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('only_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('editable', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('table_name'),
    )

    # Seed all tables that exist in the reference database
    op.execute("""
        INSERT INTO table_admin_settings (id, table_name, display_name, visible, only_admin, editable) VALUES
        (gen_random_uuid(), 'picture_attribute_reference', 'Picture Attribute Reference', true, false, true),
        (gen_random_uuid(), 'picture_attribute_reference_crosstable', 'Picture Attribute Reference Crosstable', true, true, true),
        (gen_random_uuid(), 'picture_attribute_reference_type', 'Picture Attribute Reference Type', true, false, true),
        (gen_random_uuid(), 'process_attributes', 'Process Attributes', true, true, true),
        (gen_random_uuid(), 'process_settings', 'Process Settings', true, true, true),
        (gen_random_uuid(), 'process_statuses', 'Process Statuses', true, true, true),
        (gen_random_uuid(), 'process_types', 'Process Types', true, true, true),
        (gen_random_uuid(), 'processes', 'Processes', true, true, false),
        (gen_random_uuid(), 'retail', 'Retail', true, true, true),
        (gen_random_uuid(), 'retail_process_additional', 'Retail Process Additional', true, true, true),
        (gen_random_uuid(), 'retail_processed', 'Retail Processed', true, true, false),
        (gen_random_uuid(), 'analyst_processed', 'Analyst Processed', true, true, false)
    """)


def downgrade() -> None:
    op.drop_table('table_admin_settings')
