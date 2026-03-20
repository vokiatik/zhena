import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.database import Base

class ProcessingStatus(Base):
    __tablename__ = "processing_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    message_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column("status", Text, nullable=True)
    label = Column("label", Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())