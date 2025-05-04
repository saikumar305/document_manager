from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres import get_db, get_vector_store
from app.db.models.document import Document
from app.api.deps import get_current_user
from app.schemas.qa import QARequest, QAResponse
from app.services.embedder import Embedder
from app.services.retriever import VectorDBRetriever, Retriever
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)

from app.core.config import settings


router = APIRouter()


@router.post("/", response_model=QAResponse)
def ask_question(
    data: QARequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    vector_store=Depends(get_vector_store),
):
    question = data.question
    document_id = data.document_id
    print(f"Document ID: {document_id}")
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    llm = Ollama(
        model=settings.LLM_MODEL,
        temperature=0.5,
        base_url=settings.OLLAMA_URL,
        request_timeout=120,
    )
    embed_model = OllamaEmbedding(
        model_name=settings.EMBEDDING_MODEL, base_url=settings.OLLAMA_URL
    )

    # retriever = Retriever(
    #     vector_store=vector_store,
    #     embed_model=embed_model,
    #     llm=llm,
    # )
    # nodes = retriever.retrieve(query=question)
    # answer = retriever.query_with_context(query=question)

    embedder = Embedder()
    query_embedding = embedder.embed_query(question)

    vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding, similarity_top_k=5
    )

    # query_result = vector_store.query(vector_store_query)
    # nodes = query_result.nodes

    current_doc = None
    if document_id:
        current_doc = (
            db.query(Document)
            .filter(Document.id == document_id, Document.owner_id == current_user.id)
            .first()
        )

    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="owner_id",
                value=current_user.id,
                operator=FilterOperator.EQ,
            )
        ]
    )

    retriever = VectorDBRetriever(vector_store, embedder.embed_model, filters=filters)

    query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)
    response = query_engine.query(question)

    answer = response.response
    nodes = response.source_nodes

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No answer found for the given question.",
        )

    return QAResponse(
        answer=answer,
        question=question,
        source_documents=nodes,
        document_id=document_id,
    )
