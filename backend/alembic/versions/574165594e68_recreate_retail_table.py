"""recreate retail table

Revision ID: 574165594e68
Revises: 24e27d85014e
Create Date: 2026-03-20 15:55:12.468228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '574165594e68'
down_revision: Union[str, None] = '24e27d85014e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('retail_upload_rows',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('Ретейлер clean', sa.Text(), nullable=True),
    sa.Column('Advertiser (producer)', sa.Text(), nullable=True),
    sa.Column('Brands list', sa.Text(), nullable=True),
    sa.Column('Brands list clean', sa.Text(), nullable=True),
    sa.Column('!Категория Ферреро', sa.Text(), nullable=True),
    sa.Column('!Категория Ферреро  (Range категорий)', sa.Text(), nullable=True),
    sa.Column('!Категория Ферреро (Мультибренд категорий)', sa.Text(), nullable=True),
    sa.Column('Дата первого скрина', sa.Date(), nullable=True),
    sa.Column('Дата последнего скрина', sa.Date(), nullable=True),
    sa.Column('Advertisement ID', sa.Text(), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('retail_upload_rows')
