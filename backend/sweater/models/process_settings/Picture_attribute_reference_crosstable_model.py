import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class PictureAttributeReferenceCrosstable(Base):
    __tablename__ = "picture_attribute_reference_crosstable"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    picture_attribute_id = Column(UUID(as_uuid=True), nullable=False)
    reference_value_presetting_type = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    process_id = Column(UUID(as_uuid=True), nullable=True)