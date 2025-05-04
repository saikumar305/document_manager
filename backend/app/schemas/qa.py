from pydantic import BaseModel
from typing import Optional, List, Any


class QARequest(BaseModel):
    question: str
    document_id: Optional[str]


class QAResponse(QARequest):
    answer: str
    source_documents: List[dict]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
