import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class PictureAttributeReference(Base):
    __tablename__ = "picture_attribute_reference"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_value = Column(Text, nullable=False)
    reference_type_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
