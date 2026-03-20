import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sweater.database.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    chat_id = Column(UUID(as_uuid=True), nullable=False)

    role = Column("role", Text, nullable=True)
    content = Column("content", Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())