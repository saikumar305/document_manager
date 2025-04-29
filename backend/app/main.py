from fastapi import FastAPI
import uvicorn
from app.db.postgres import async_session, engine
from app.db.base import Base
from app.db import models # Import your models here

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
