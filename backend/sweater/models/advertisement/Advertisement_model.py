import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class Advertisement(Base):
    __tablename__ = "advertisement"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), nullable=True)

    # Data fields – FK references into simple_value
    retailer_clean_id = Column(UUID(as_uuid=True), nullable=True)
    advertiser_id = Column(UUID(as_uuid=True), nullable=True)
    brand_id = Column(UUID(as_uuid=True), nullable=True)
    product_category_id = Column(UUID(as_uuid=True), nullable=True)
    brand_category_id = Column(UUID(as_uuid=True), nullable=True)

    first_appearance_date = Column(Date, nullable=True)
    last_appearance_date = Column(Date, nullable=True)

    # Technical fields
    data_type = Column(Text, nullable=True)   # 'file' | 'link'
    verified = Column(Boolean, nullable=False, default=False)
    declined = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
