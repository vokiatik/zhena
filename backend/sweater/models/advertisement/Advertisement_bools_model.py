import uuid
from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class AdvertisementBools(Base):
    """Boolean flags associated with one advertisement row."""
    __tablename__ = "advertisement_bools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    add_id = Column(UUID(as_uuid=True), nullable=False)  # FK → advertisement.id
    key_player = Column(Boolean, nullable=True)
    referent_market = Column(Boolean, nullable=True)
    packed_chocolate = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
