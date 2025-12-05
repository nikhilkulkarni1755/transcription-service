from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Video Transcription Service",
    description="Download YouTube videos and transcribe them using HuggingFace models",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1", tags=["transcription"])


@app.get("/")
async def root():
    return {"message": "Video Transcription Service is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
