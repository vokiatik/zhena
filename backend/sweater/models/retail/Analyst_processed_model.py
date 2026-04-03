import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class AnalystProcessed(Base):
    __tablename__ = "analyst_processed"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    format = Column(Text, nullable=True)
    weekly_price = Column(Text, nullable=True)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    process_id = Column(UUID(as_uuid=True), nullable=False)
    retail_processed_id = Column(UUID(as_uuid=True), nullable=False)
    link = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
