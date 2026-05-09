"""update_table_admin_settings

Revision ID: g4h5i6j7k8l9
Revises: c183b5255915
Create Date: 2026-05-07 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g4h5i6j7k8l9'
down_revision: Union[str, Sequence[str], None] = 'c183b5255915'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove stale entries for tables that no longer exist
    op.execute("""
        DELETE FROM table_admin_settings
        WHERE table_name IN ('picture_attribute_reference_crosstable', 'retail_process_additional')
    """)

    # Add entries for new tables created after the initial seed
    op.execute("""
        INSERT INTO table_admin_settings (id, table_name, display_name, visible, only_admin, editable)
        VALUES
        (gen_random_uuid(), 'ecom_format', 'Ecom Format', true, true, true),
        (gen_random_uuid(), 'ecom_format_for_detector', 'Ecom Format For Detector', true, true, true)
        ON CONFLICT (table_name) DO NOTHING
    """)


def downgrade() -> None:
    # Remove the newly added entries
    op.execute("""
        DELETE FROM table_admin_settings
        WHERE table_name IN ('ecom_format', 'ecom_format_for_detector')
    """)

    # Restore the removed entries
    op.execute("""
        INSERT INTO table_admin_settings (id, table_name, display_name, visible, only_admin, editable)
        VALUES
        (gen_random_uuid(), 'picture_attribute_reference_crosstable', 'Picture Attribute Reference Crosstable', true, true, true),
        (gen_random_uuid(), 'retail_process_additional', 'Retail Process Additional', true, true, true)
        ON CONFLICT (table_name) DO NOTHING
    """)
