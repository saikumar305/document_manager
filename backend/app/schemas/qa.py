from pydantic import BaseModel, Field
from typing import Optional, List, Any


class QA(BaseModel):
    """QA schema."""

    question: str = Field(..., description="The question to be asked.")
    answer: Optional[str] = Field(None, description="The answer to the question.")
    document_id: str = Field(..., description="The ID of the document related to the question.")
    metadata: Optional[List[dict[str, Any]]] = Field(
        None, description="Additional metadata related to the QA."
    )

    class Config:
        """Pydantic config."""

        orm_mode = True
        json_encoders = {
            Any: lambda v: v.isoformat() if isinstance(v, Any) else None
        }
        schema_extra = {
            "example": {
                "question": "What is the capital of France?",
                "answer": "The capital of France is Paris.",
                "document_id": "12345",
                "metadata": [{"key": "source", "value": "Wikipedia"}],
            }
        }
        