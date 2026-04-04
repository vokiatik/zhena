"""
DEV-ONLY: Drop all tables and recreate from SQLAlchemy models.
Usage:  python reset_db.py          # reset both databases
        python reset_db.py main     # reset main only
        python reset_db.py ref      # reset reference only
"""

import sys
from dotenv import load_dotenv

load_dotenv()

from sweater.database.base_db import Base, engine

# -- import every model so Base.metadata knows about them --
from sweater.models.auth.User_model import UserModel
from sweater.models.auth.Email_confirmations_model import EmailConfirmation
from sweater.models.auth.Password_reset_model import PasswordReset
from sweater.models.auth.Role_model import RoleModel, UserRoleModel
from sweater.models.chat.Chat_model import Chat
from sweater.models.chat.Message_model import Message
from sweater.models.chat.Processing_status_model import ProcessingStatus
from sweater.models.file_processing.File_processing_model import FileProcessing
from sweater.models.logging.Picture_processing_history import PictureHistory

from sweater.database.references_db import Reference_Base, reference_engine

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

from sqlalchemy import text


def reset_main():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Main DB reset")


def reset_reference():
    with reference_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    Reference_Base.metadata.drop_all(bind=reference_engine)
    Reference_Base.metadata.create_all(bind=reference_engine)
    print("✓ Reference DB reset")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target in ("all", "main"):
        reset_main()
    if target in ("all", "ref"):
        reset_reference()
