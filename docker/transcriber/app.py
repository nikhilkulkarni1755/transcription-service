from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch
import yt_dlp
import tempfile
import os

app = FastAPI(title="Transcription Service")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

transcriber = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",
    device=device
)


class TranscribeRequest(BaseModel):
    video_url: str


class TranscribeResponse(BaseModel):
    transcription: str


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_video(request: TranscribeRequest):
    """
    Stream audio from video URL and transcribe using HuggingFace Whisper model.
    No video file is saved to disk - audio is streamed directly to transcription.
    """
    temp_audio_file = None
    try:
        print(f"Processing video URL: {request.video_url}")

        # Create a temporary file for the audio
        temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_audio_path = temp_audio_file.name
        temp_audio_file.close()

        # Configure yt-dlp to extract only audio (no video download)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': temp_audio_path.replace('.wav', ''),
            'quiet': False,
            'no_warnings': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }

        print("Streaming audio from video...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.video_url])

        # Transcribe the audio
        print(f"Transcribing audio...")
        result = transcriber(temp_audio_path, return_timestamps=True, chunk_length_s=30)
        transcription_text = result["text"]
        print(f"Transcription complete: {len(transcription_text)} characters")

        return TranscribeResponse(transcription=transcription_text)

    except Exception as e:
        print(f"Transcription error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

    finally:
        # Clean up temporary audio file immediately after transcription
        if temp_audio_file and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                print(f"Cleaned up temporary audio file: {temp_audio_path}")
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "transcriber", "device": device}


@app.on_event("startup")
async def startup_event():
    print("Transcription service started")
    print(f"Model loaded on device: {device}")
    print("Ready to stream and transcribe videos")
