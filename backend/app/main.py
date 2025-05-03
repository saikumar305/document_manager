from fastapi import FastAPI
import uvicorn
from sqlalchemy import text
from app.db.postgres import engine
from app.db.base import Base
from app.db import models

from app.api.auth import router as auth_router
from app.api.document import router as document_router


app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(document_router, prefix="/documents", tags=["documents"])
# Import your models here to ensure they are registered with SQLAlchemy


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
