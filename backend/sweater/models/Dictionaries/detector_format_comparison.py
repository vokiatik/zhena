import uuid
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class DetectorFormatComparison(Base):
    """Replaces ecom_format_for_detector.
    Maps raw detector strings to the canonical format table."""
    __tablename__ = "detector_format_comparison"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_id = Column(UUID(as_uuid=True), nullable=False)  # FK → retailer.id
    detector_format = Column(Text, nullable=True)
    format_id = Column(UUID(as_uuid=True), nullable=True)  # FK → format.id
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
