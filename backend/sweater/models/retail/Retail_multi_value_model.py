import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class RetailMultiValue(Base):
    __tablename__ = "retail_multi_values"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    picture_id = Column(UUID(as_uuid=True), nullable=False)
    field_name = Column(Text, nullable=False)
    value = Column(UUID, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
