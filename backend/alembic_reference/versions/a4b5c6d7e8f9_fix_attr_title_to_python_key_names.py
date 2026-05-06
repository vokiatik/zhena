"""fix_attr_title_to_python_key_names

Revision ID: a4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-05-06 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b5c6d7e8f9'
down_revision: Union[str, Sequence[str], None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mapping: DB column name (col.name) -> Python attribute name (col.key)
COLUMN_NAME_MAP = [
    ("Ретейлер clean",                               "retailer_clean"),
    ("Advertiser (producer)",                        "advertiser_producer"),
    ("Brands list",                                  "brands_list"),
    ("Brands list clean",                            "brands_list_clean"),
    ("!Категория Ферреро",                           "ferrero_category"),
    ("!Категория Ферреро  (Range категорий)",         "ferrero_category_range"),
    ("!Категория Ферреро (Мультибренд категорий)",   "ferrero_category_multibrand"),
    ("Дата первого скрина",                          "first_screen_date"),
    ("Дата последнего скрина",                       "last_screen_date"),
    ("Advertisement ID",                             "advertisement_id"),
]


def upgrade() -> None:
    for old_name, new_name in COLUMN_NAME_MAP:
        op.execute(
            sa.text(
                "UPDATE process_attributes SET title = :new WHERE title = :old"
            ).bindparams(old=old_name, new=new_name)
        )


def downgrade() -> None:
    for old_name, new_name in COLUMN_NAME_MAP:
        op.execute(
            sa.text(
                "UPDATE process_attributes SET title = :old WHERE title = :new"
            ).bindparams(old=old_name, new=new_name)
        )
