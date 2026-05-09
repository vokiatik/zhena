import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class EcomFormatForDetector(Base):
    __tablename__ = "ecom_format_for_detector"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    retailer_id = Column(UUID, nullable=True)
    format_detector = Column(Text, nullable=True)
    format= Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())