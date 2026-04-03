import uuid
from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class ProcessAttributes(Base):
    __tablename__ = "process_attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column("title", Text, nullable=True)
    is_shown = Column(Boolean, nullable=False, default=True)
    is_editable = Column(Boolean, nullable=False, default=True)
    reference_type_id = Column(UUID(as_uuid=True), nullable=True)
    process_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())