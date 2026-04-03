import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class ProcessType(Base):
    __tablename__ = "process_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_type_name = Column(Text, nullable=False)
    table_name = Column(Text, nullable=True)
