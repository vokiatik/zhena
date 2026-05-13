import uuid
from sqlalchemy import Column, DateTime, Text, FLOAT, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class Format(Base):
    """Replaces ecom_format.
    funnel_stage_id now points to a simple_value row of type 'funnel_stage'."""
    __tablename__ = "format"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_id = Column(UUID(as_uuid=True), nullable=True)   # FK → simple_value.id (retailer_clean)
    format = Column(Text, nullable=True)
    funnel_stage_id = Column(UUID(as_uuid=True), nullable=True) # FK → simple_value.id (funnel_stage)
    sov = Column(FLOAT, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
