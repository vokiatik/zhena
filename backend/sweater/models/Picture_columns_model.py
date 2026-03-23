import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from backend.sweater.database.base_db import Base

class PictureColumns(Base):
    __tablename__ = "picture_columns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column("title", Text, nullable=True)
    is_shown = Column(Boolean, nullable=False, default=True)
    is_editable = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    file_id = Column(UUID(as_uuid=True), nullable=False)