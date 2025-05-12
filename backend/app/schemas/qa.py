from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class QARequest(BaseModel):
    question: str
    document_id: Optional[str]


class QAResponse(QARequest):
    answer: str
    source_documents: List[dict]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class QAHistory(BaseModel):
    document_id: str
    question: str
    answer: str
    source_documents: List[dict]
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
