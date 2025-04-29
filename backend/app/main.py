from fastapi import FastAPI
import uvicorn
from app.db.postgres import engine
from app.db.base import Base
from app.db import models  # Import your models here

from app.api.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
