import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from backend.sweater.database.base_db import Base

class RetailAdditional(Base):
    __tablename__ = "retail_upload_rows_additional"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    retail_upload_row_id = Column(UUID(as_uuid=True), nullable=False)
    key_player = Column("Key player", Boolean, default=False, nullable=False)
    referent_market = Column("Referent Market", Boolean, default=False, nullable=False)
    packed_chocolate = Column("Packed Chocolate", Boolean, default=False, nullable=False)

    # Advertising category	Seasonal	!Формат	Количество дней размещения est.	group_id

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())