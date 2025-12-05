from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import os
from pathlib import Path

app = FastAPI(title="Video Downloader Service")

DOWNLOAD_DIR = Path("/downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


class DownloadRequest(BaseModel):
    video_url: str


class DownloadResponse(BaseModel):
    audio_file_path: str
    title: str


@app.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest):
    """
    Download video from URL and extract audio.
    """
    try:
        output_template = str(DOWNLOAD_DIR / "%(id)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.video_url, download=True)
            video_id = info['id']
            title = info.get('title', 'Unknown')
            audio_file = DOWNLOAD_DIR / f"{video_id}.wav"

            if not audio_file.exists():
                raise HTTPException(status_code=500, detail="Audio file not created")

            return DownloadResponse(
                audio_file_path=str(audio_file),
                title=title
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "downloader"}
