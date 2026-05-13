import uuid
from sqlalchemy import Column, DateTime, FLOAT, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class AdvertisementPrice(Base):
    """Weekly/unit price associated with one advertisement row."""
    __tablename__ = "advertisement_price"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    add_id = Column(UUID(as_uuid=True), nullable=False)  # FK → advertisement.id
    price = Column(FLOAT, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
