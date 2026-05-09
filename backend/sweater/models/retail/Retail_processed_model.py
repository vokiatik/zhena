import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base


class RetailProcessed(Base):
    __tablename__ = "retail_processed"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    retailer_clean = Column(Text, nullable=False)
    advertiser_producer = Column(Text, nullable=False)
    brands_list_clean = Column(Text, nullable=False)
    ferrero_category_range = Column(Text, nullable=False)
    ferrero_category_multibrand = Column(Text, nullable=False)
    first_screen_date = Column(Date, nullable=False)
    last_screen_date = Column(Date, nullable=False)
    advertisement_id = Column(Text, nullable=False)
    advertising_category = Column(Text, nullable=True)
    seasonal = Column(Boolean, nullable=True)
    format = Column(Text, nullable=False)
    estimated_days = Column(Text, nullable=False)
    group_id = Column(Text, nullable=True)
    
    user_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(Text, nullable=False)
    process_id = Column(UUID(as_uuid=True), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
