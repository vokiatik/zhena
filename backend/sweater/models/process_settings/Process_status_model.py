import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class ProcessStatus(Base):
    __tablename__ = "process_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_status_name = Column(Text, nullable=False)
