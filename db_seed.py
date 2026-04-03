"""
Seed the reference database with default process types and statuses.
Idempotent – skips rows that already exist.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

REFERENCE_DATABASE_URL = os.getenv(
    "REFERENCE_DATABASE_URL",
    "postgresql+psycopg2://app:app@localhost:5432/text_analyser_reference",
)

PROCESS_TYPES = [
    ("file", "retail_processed"),
    ("link", "retail_processed"),
    ("analyst", "analyst_processed"),
]

PROCESS_STATUSES = [
    "initiated",
    "in progress",
    "done",
]


def seed():
    engine = create_engine(REFERENCE_DATABASE_URL)

    with engine.begin() as conn:
        for name, table_name in PROCESS_TYPES:
            exists = conn.execute(
                text("SELECT 1 FROM process_types WHERE process_type_name = :name"),
                {"name": name},
            ).scalar()
            if not exists:
                conn.execute(
                    text("INSERT INTO process_types (id, process_type_name, table_name) VALUES (gen_random_uuid(), :name, :table_name)"),
                    {"name": name, "table_name": table_name},
                )
                print(f"  Inserted process type: {name}")
            else:
                # Update table_name if not set
                conn.execute(
                    text("UPDATE process_types SET table_name = :table_name WHERE process_type_name = :name AND (table_name IS NULL OR table_name = '')"),
                    {"name": name, "table_name": table_name},
                )
                print(f"  Process type already exists: {name}")

        # Fix old "flink" type if present
        conn.execute(
            text("UPDATE process_types SET process_type_name = 'link', table_name = 'retail_processed' WHERE process_type_name = 'flink'"),
        )

        for name in PROCESS_STATUSES:
            exists = conn.execute(
                text("SELECT 1 FROM process_statuses WHERE process_status_name = :name"),
                {"name": name},
            ).scalar()
            if not exists:
                conn.execute(
                    text("INSERT INTO process_statuses (id, process_status_name) VALUES (gen_random_uuid(), :name)"),
                    {"name": name},
                )
                print(f"  Inserted process status: {name}")
            else:
                print(f"  Process status already exists: {name}")

    engine.dispose()
    print("Seed complete.")


if __name__ == "__main__":
    seed()
