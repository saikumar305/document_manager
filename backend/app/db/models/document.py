from app.db.base import Base
from sqlalchemy import Boolean, Column, Integer, String , ForeignKey, DateTime, Text
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # NEW: relationship back to User
    owner = relationship("User", back_populates="documents")
