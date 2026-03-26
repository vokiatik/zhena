import os
import subprocess
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REFERENCE_DATABASE_URL = os.getenv("REFERENCE_DATABASE_URL")

if not DATABASE_URL or not REFERENCE_DATABASE_URL:
    raise RuntimeError("Missing DB URLs")

def ensure_database_exists(database_url: str) -> None:
    url = make_url(database_url)
    db_name = url.database

    if not db_name:
        raise RuntimeError("Database name is missing in DATABASE_URL")

    # connect to a maintenance DB first
    admin_url = url.set(database="postgres")

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name},
            ).scalar()

            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"Database '{db_name}' created.")
            else:
                print(f"Database '{db_name}' already exists.")
    finally:
        engine.dispose()

ensure_database_exists(DATABASE_URL)
ensure_database_exists(REFERENCE_DATABASE_URL)