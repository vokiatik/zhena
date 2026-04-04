import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class PictureAttributeReferenceType(Base):
    __tablename__ = "picture_attribute_reference_type"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_type_name = Column(Text, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
