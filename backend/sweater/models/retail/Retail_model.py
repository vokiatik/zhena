import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.references_db import Reference_Base as Base

class Retail(Base):
    __tablename__ = "retail"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), nullable=True)

    retailer_clean = Column("Ретейлер clean", Text, nullable=True)
    advertiser_producer = Column("Advertiser (producer)", Text, nullable=True)
    brands_list = Column("Brands list", Text, nullable=True)
    brands_list_clean = Column("Brands list clean", Text, nullable=True)
    ferrero_category = Column("!Категория Ферреро", Text, nullable=True)
    ferrero_category_range = Column("!Категория Ферреро  (Range категорий)", Text, nullable=True)
    ferrero_category_multibrand = Column("!Категория Ферреро (Мультибренд ка", Text, nullable=True)
    first_screen_date = Column("Дата первого скрина", Date, nullable=True)
    last_screen_date = Column("Дата последнего скрина", Date, nullable=True)
    advertisement_id = Column("Advertisement ID", Text, nullable=True)

    advertising_category = Column("advertising_category", Text, nullable=True)
    is_seasonal = Column("is_seasonal", Boolean, nullable=True)
    format = Column("format", Text, nullable=True)
    days_monitored_est = Column("days_monitored_est", Integer, nullable=True)
    group_id = Column("group_id", Text, nullable=True)

    verified = Column(Boolean, nullable=False, default=False)
    declined = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

EXPECTED_COLUMNS = [
    "Ретейлер clean",
    "Advertiser (producer)",
    "Brands list",
    "Brands list clean",
    "!Категория Ферреро",
    "!Категория Ферреро  (Range категорий)",
    "!Категория Ферреро (Мультибренд категорий)",
    "Дата первого скрина",
    "Дата последнего скрина",
    "Advertisement ID",
    "Advertising category",
    "Seasonal",
    "!Формат",
    "Количество дней размещения est.",
    "group_id",
]

FILE_COL_TO_DB_COL = {
    "Ретейлер clean": "retailer_clean",
    "Advertiser (producer)": "advertiser_producer",
    "Brands list": "brands_list",
    "Brands list clean": "brands_list_clean",
    "!Категория Ферреро": "ferrero_category",
    "!Категория Ферреро  (Range категорий)": "ferrero_category_range",
    "!Категория Ферреро (Мультибренд категорий)": "ferrero_category_multibrand",
    "Дата первого скрина": "first_screen_date",
    "Дата последнего скрина": "last_screen_date",
    "Advertisement ID": "advertisement_id",
    "Advertising category": "advertising_category",
    "Seasonal": "seasonal",
    "!Формат": "format",
    "Количество дней размещения est.": "estimated_days",
    "group_id": "group_id",
}