import uuid
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class AdvertisementAddCategory(Base):
    """Advertising categories associated with one advertisement row."""
    __tablename__ = "advertisement_add_category"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    add_id = Column(UUID(as_uuid=True), nullable=False)          # FK → advertisement.id
    add_category_id = Column(UUID(as_uuid=True), nullable=False) # FK → simple_value.id
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
