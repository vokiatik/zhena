import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class SOV(Base):
    __tablename__ = "SOV"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    retailer_name = Column(Text, nullable=True)
    format = Column(Text, nullable=True)
    stage = Column(Text, nullable=True)
    sov = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())