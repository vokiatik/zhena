"""fix_input_type_for_existing_dropdown_attributes

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-05-06 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Any attribute that already had a reference_type_id set was
    # effectively a "dropdown". Set input_type accordingly so the
    # frontend condition `inputType === "dropdown"` still matches them.
    op.execute(
        sa.text(
            "UPDATE process_attributes "
            "SET input_type = 'dropdown' "
            "WHERE reference_type_id IS NOT NULL AND input_type = 'text'"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE process_attributes "
            "SET input_type = 'text' "
            "WHERE reference_type_id IS NOT NULL AND input_type = 'dropdown'"
        )
    )
