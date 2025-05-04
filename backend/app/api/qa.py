from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres import get_db, get_vector_store
from app.api.deps import get_current_user
from app.schemas.qa import QA
from app.services.embedder import Embedder
from app.services.retriever import VectorDBRetriever, Retriever
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters


router = APIRouter()


@router.post("/")
def ask_question(
    question: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    vector_store=Depends(get_vector_store),
):
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    llm = Ollama(model="llama3.1", temperature=0.5)
    embed_model = OllamaEmbedding(model_name="nomic-embed-text:v1.5")

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

    query_result = vector_store.query(vector_store_query)
    nodes = query_result.nodes

    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="owner_id",
                value=current_user.id,
                operator="eq",
            ),
            MetadataFilter(
                key="document_id",
                value=document_id,
                operator="eq",
            ),
        ]
    )

    retriever = VectorDBRetriever(vector_store, embedder.embed_model)

    llm = Ollama(model="llama3.1", temperature=0.5)

    query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)

    answer = query_engine.query(question)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No answer found for the given question.",
        )

    return {"question": question, "answer": str(answer), "nodes": nodes}
