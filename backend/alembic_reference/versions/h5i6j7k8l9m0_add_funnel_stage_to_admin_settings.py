"""add_funnel_stage_to_admin_settings

Revision ID: h5i6j7k8l9m0
Revises: g4h5i6j7k8l9
Create Date: 2026-05-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h5i6j7k8l9m0'
down_revision: Union[str, Sequence[str], None] = '6e318eec7643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO table_admin_settings (id, table_name, display_name, visible, only_admin, editable)
        VALUES
        (gen_random_uuid(), 'funnel_stage', 'Funnel Stage', true, true, true)
        ON CONFLICT (table_name) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM table_admin_settings
        WHERE table_name = 'funnel_stage'
    """)
