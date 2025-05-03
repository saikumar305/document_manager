from app.db.base import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey
from pgvector.sqlalchemy import Vector

from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    owner_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # NEW: relationship back to User
    owner = relationship("User", back_populates="documents")


# class DocumentEmbedding(Base):
#     __tablename__ = "document_embeddings"

#     id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     document_id = Column(
#         String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
#     )
#     embedding = Column(Vector(768))
#     created_at = Column(DateTime, default=datetime.utcnow)
