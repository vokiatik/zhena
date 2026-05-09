import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class TableAdminSettings(Base):
    __tablename__ = "table_admin_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(Text, nullable=False, unique=True)
    display_name = Column(Text, nullable=False)
    visible = Column(Boolean, nullable=False, default=True)
    only_admin = Column(Boolean, nullable=False, default=False)
    editable = Column(Boolean, nullable=False, default=True)
    uploadable = Column(Boolean, nullable=False, default=False)
    upload_prefix = Column(Text, nullable=True)  # If not null, only files with names starting with this prefix can be uploaded for the table
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
