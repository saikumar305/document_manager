import os
from dotenv import load_dotenv

load_dotenv()  # load .env if present


class Settings:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1  # 1 days
    ALGORITHM = "HS256"

    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
    CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:v1.5")


settings = Settings()

print("Settings loaded:" , settings.__dict__)
