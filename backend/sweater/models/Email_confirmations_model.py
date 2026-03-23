import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from backend.sweater.database.base_db import Base

class EmailConfirmation(Base):
    __tablename__ = "email_confirmations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False)

    token = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, 
    server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)