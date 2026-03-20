"""recreate users table

Revision ID: 24e27d85014e
Revises: f823c0ccc99b
Create Date: 2026-03-20 15:54:06.789844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24e27d85014e'
down_revision: Union[str, None] = 'f823c0ccc99b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
