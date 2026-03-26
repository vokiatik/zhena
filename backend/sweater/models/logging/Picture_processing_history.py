import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.base_db import Base

class PictureHistory(Base):
    __tablename__ = "picture_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    picture_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    confirmed = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
