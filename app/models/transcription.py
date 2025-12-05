from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class TranscriptionStatus(str, enum.Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transcription(Base):
    __tablename__ = "transcriptions"

    video_url = Column(String, primary_key=True, index=True)
    status = Column(Enum(TranscriptionStatus), default=TranscriptionStatus.PENDING)
    transcription_text = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
