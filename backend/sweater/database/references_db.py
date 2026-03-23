import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

REFERENCE_DATABASE_URL = os.getenv(
    "REFERENCE_DATABASE_URL",
    "postgresql+psycopg2://app:app@localhost:5432/text_analyser_reference",
)

reference_engine = create_engine(REFERENCE_DATABASE_URL, pool_pre_ping=True)
Reference_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=reference_engine)
Reference_Base = declarative_base()


def get_db():
    db = Reference_SessionLocal()
    try:
        yield db
    finally:
        db.close()