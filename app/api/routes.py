from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, async_session_maker
from app.models import Transcription, TranscriptionStatus
from app.api.schemas import TranscriptionRequest, TranscriptionResponse
from app.services import TranscriptionModelService

router = APIRouter()
transcription_service = TranscriptionModelService()


async def process_transcription(video_url: str):
    """
    Background task to stream and transcribe video.
    Creates its own database session.
    """
    try:
        # Update status to TRANSCRIBING
        async with async_session_maker() as db:
            result = await db.execute(
                select(Transcription).where(Transcription.video_url == video_url)
            )
            transcription = result.scalar_one_or_none()

            if not transcription:
                return

            transcription.status = TranscriptionStatus.TRANSCRIBING
            await db.commit()

        # Stream audio and transcribe (no files saved)
        transcription_result = await transcription_service.transcribe_video(video_url)
        transcription_text = transcription_result.get("transcription")

        # Update status to COMPLETED
        async with async_session_maker() as db:
            result = await db.execute(
                select(Transcription).where(Transcription.video_url == video_url)
            )
            transcription = result.scalar_one_or_none()
            transcription.transcription_text = transcription_text
            transcription.status = TranscriptionStatus.COMPLETED
            await db.commit()

    except Exception as e:
        # Update status to FAILED
        async with async_session_maker() as db:
            result = await db.execute(
                select(Transcription).where(Transcription.video_url == video_url)
            )
            transcription = result.scalar_one_or_none()
            if transcription:
                transcription.status = TranscriptionStatus.FAILED
                transcription.error_message = str(e)
                await db.commit()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a video URL for transcription.
    If already transcribed, returns existing result.
    Otherwise, starts async processing.
    """
    result = await db.execute(
        select(Transcription).where(Transcription.video_url == request.video_url)
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.status == TranscriptionStatus.COMPLETED:
            return existing
        else:
            return existing

    new_transcription = Transcription(
        video_url=request.video_url,
        status=TranscriptionStatus.PENDING
    )
    db.add(new_transcription)
    await db.commit()
    await db.refresh(new_transcription)

    background_tasks.add_task(process_transcription, request.video_url)

    return new_transcription


@router.get("/transcription/{video_url:path}", response_model=TranscriptionResponse)
async def get_transcription(
    video_url: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status and result of a transcription by video URL.
    """
    result = await db.execute(
        select(Transcription).where(Transcription.video_url == video_url)
    )
    transcription = result.scalar_one_or_none()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    return transcription
