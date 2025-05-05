from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentOut(BaseModel):
    id: str
    title: str
    content: Optional[str]
    file_name: str
    owner_id: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else None
        }


class QA(BaseModel):
    question: str
    answer: Optional[str]
    document_id: str

    class Config:
        orm_mode = True
       