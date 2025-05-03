from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

from llama_index.vector_stores.postgres import PGVectorStore


DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


vector_store = PGVectorStore.from_params(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    database=settings.POSTGRES_DB,
    table_name="document_embeddings",
    embed_dim=768,
)


def get_vector_store():
    return vector_store
