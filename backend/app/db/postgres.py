from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings


DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db():
    with SessionLocal() as session:
        yield session
