"""add is_incorrect to advertisement_link

Revision ID: j7k8l9m0n1o2
Revises: i6j7k8l9m0n1
Create Date: 2026-05-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'j7k8l9m0n1o2'
down_revision = '01c02b3e9d72'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'advertisement_link',
        sa.Column('is_incorrect', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('advertisement_link', 'is_incorrect')
