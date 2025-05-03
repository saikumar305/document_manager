from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres import get_db, get_vector_store
from app.api.deps import get_current_user
from app.schemas.qa import QA
from app.services.embedder import Embedder
from app.services.retriever import VectorDBRetriever
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.vector_stores import VectorStoreQuery


router = APIRouter()


@router.post("/")
def ask_question(
    question: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    vector_store=Depends(get_vector_store),
):
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    embedder = Embedder()
    query_embedding = embedder.embed_query(question)

    vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding, similarity_top_k=2
    )

    query_result = vector_store.query(vector_store_query)
    print(query_result.nodes[0].get_content())

    retriever = VectorDBRetriever(vector_store, embedder.embed_model)

    llm = Ollama(model="llama3.1", temperature=0.5)

    query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)

    answer = query_engine.query(question)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No answer found for the given question.",
        )

    return {"question": question, "answer": str(answer)}
