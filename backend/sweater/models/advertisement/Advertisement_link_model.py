import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class AdvertisementLink(Base):
    __tablename__ = "advertisement_link"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    add_id = Column(UUID(as_uuid=True), nullable=False)   # FK → advertisement.id
    link = Column(Text, nullable=True)
    appearance_period = Column(Text, nullable=True)
    is_incorrect = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
