from pydantic import BaseModel, HttpUrl
from datetime import datetime
from app.models import TranscriptionStatus


class TranscriptionRequest(BaseModel):
    video_url: str


class TranscriptionResponse(BaseModel):
    video_url: str
    status: TranscriptionStatus
    transcription_text: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
