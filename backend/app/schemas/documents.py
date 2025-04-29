from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class DocumentIn(BaseModel):
    title: str
    content: str


class DocumentOut(DocumentIn):
    id: UUID
    owner_id: UUID
    created_at: datetime
