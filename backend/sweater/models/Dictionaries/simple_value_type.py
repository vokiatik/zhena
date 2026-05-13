import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


# Allowed field_name values (stored as plain text):
#   advertiser, brand, add_category, product_category,
#   brand_category, retailer_clean, funnel_stage

class SimpleValueType(Base):
    """Enumerates the category types that simple_value rows belong to."""
    __tablename__ = "simple_value_type"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
