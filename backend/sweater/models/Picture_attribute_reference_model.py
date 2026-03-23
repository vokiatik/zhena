import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from backend.sweater.database.base_db import Base

class PictureAttributeReference(Base):
    __tablename__ = "picture_attribute_reference"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    picture_attribute_id = Column(UUID(as_uuid=True), nullable=False)
    reference_table_name = Column(Text, nullable=False)
    reference_column_name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
