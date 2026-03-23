import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from backend.sweater.database.base_db import Base

class FileProcessing(Base):
    __tablename__ = "file_processing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column("title", Text, nullable=True)
    
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    responsible_user_id = Column(UUID(as_uuid=True), nullable=False)