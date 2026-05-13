import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class SimpleValue(Base):
    """Replaces picture_attribute_reference.
    Stores named dictionary values grouped by type."""
    __tablename__ = "simple_value"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    column_name_id = Column(UUID(as_uuid=True), nullable=False)  # FK → simple_value_type.id
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
