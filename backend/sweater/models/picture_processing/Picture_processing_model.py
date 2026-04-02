import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class PictureProcessing(Base):
    __tablename__ = "picture_processing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column("title", Text, nullable=True)
    description = Column("description", Text, nullable=True)
    table_name = Column(Text, nullable=False, server_default="retail")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())