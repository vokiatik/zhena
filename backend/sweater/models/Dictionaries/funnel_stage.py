import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class FunnelStage(Base):
    __tablename__ = "funnel_stage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    funnel_stage_name = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())