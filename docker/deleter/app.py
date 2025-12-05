from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import os

app = FastAPI(title="Video Deleter Service")

DOWNLOAD_DIR = Path("/downloads")


class DeleteRequest(BaseModel):
    audio_file_path: str


class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_file: str


@app.post("/delete", response_model=DeleteResponse)
async def delete_video(request: DeleteRequest):
    """
    Delete audio/video file to free up space.
    """
    try:
        file_path = Path(request.audio_file_path)

        # Security check: ensure file is within the downloads directory
        if not str(file_path).startswith(str(DOWNLOAD_DIR)):
            raise HTTPException(
                status_code=400,
                detail="File path must be within downloads directory"
            )

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {request.audio_file_path}"
            )

        # Get file size before deletion for logging
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        # Delete the file
        os.remove(file_path)

        message = f"Successfully deleted {file_path.name} ({file_size_mb:.2f} MB)"
        print(message)

        return DeleteResponse(
            success=True,
            message=message,
            deleted_file=str(file_path)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "deleter"}
