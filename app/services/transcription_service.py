import httpx


class TranscriptionModelService:
    def __init__(self, transcriber_url: str = "http://transcriber:8002"):
        self.transcriber_url = transcriber_url
        self.client = httpx.AsyncClient(timeout=600.0)

    async def transcribe_video(self, video_url: str) -> dict:
        """
        Send video URL to the transcription service running in Docker.
        The service will stream the audio and transcribe it without saving files.
        Returns the transcribed text.
        """
        try:
            response = await self.client.post(
                f"{self.transcriber_url}/transcribe",
                json={"video_url": video_url}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Transcription service error: {str(e)}")

    async def close(self):
        await self.client.aclose()
