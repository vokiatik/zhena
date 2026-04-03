import uuid
from sqlalchemy import Column, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class Process(Base):
    __tablename__ = "processes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_id = Column(UUID(as_uuid=True), nullable=False)
    status_id = Column(UUID(as_uuid=True), nullable=True)
    comment = Column(Text, nullable=True)
    initiator_id = Column(UUID(as_uuid=True), nullable=True)
    total_items = Column(Integer, nullable=True)
    parent_process_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
