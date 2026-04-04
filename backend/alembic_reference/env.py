from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool


from dotenv import load_dotenv

from alembic import context

from sweater.database.references_db import Reference_Base

from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType
from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.process_settings.Process_attributes_crosstable_model import ProcessAttributes
from sweater.models.process_settings.Picture_processing_model import ProcessSettings
from sweater.models.process_settings.Process_type_model import ProcessType
from sweater.models.process_settings.Process_status_model import ProcessStatus
from sweater.models.process_settings.Process_model import Process
from sweater.models.retail.Retail_model import Retail
from sweater.models.retail.Retail_model_additional import RetailAdditional
from sweater.models.retail.Retail_processed_model import RetailProcessed
from sweater.models.retail.Analyst_processed_model import AnalystProcessed

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

REFERENCE_DATABASE_URL = os.getenv("REFERENCE_DATABASE_URL")

if not REFERENCE_DATABASE_URL:
    raise RuntimeError("REFERENCE_DATABASE_URL is not set")

config.set_main_option("sqlalchemy.url", REFERENCE_DATABASE_URL)

target_metadata = Reference_Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
