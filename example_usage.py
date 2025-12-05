"""
Example usage of the Video Transcription Service API.
Make sure the service is running with: docker-compose up
"""
import httpx
import asyncio
import time
from urllib.parse import quote


async def main():
    base_url = "http://localhost:8000/api/v1"
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"Submitting video for transcription: {video_url}")

        response = await client.post(
            f"{base_url}/transcribe",
            json={"video_url": video_url}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\nStatus: {result['status']}")
            print(f"Created at: {result['created_at']}")

            encoded_url = quote(video_url, safe='')

            print("\nPolling for transcription status...")
            max_attempts = 60
            attempt = 0

            while attempt < max_attempts:
                attempt += 1
                time.sleep(5)

                status_response = await client.get(
                    f"{base_url}/transcription/{encoded_url}"
                )

                if status_response.status_code == 200:
                    status_result = status_response.json()
                    current_status = status_result['status']
                    print(f"Attempt {attempt}: Status = {current_status}")

                    if current_status == "completed":
                        print("\nTranscription completed!")
                        print(f"\nTranscription text:\n{status_result['transcription_text']}")
                        break
                    elif current_status == "failed":
                        print(f"\nTranscription failed: {status_result['error_message']}")
                        break
                else:
                    print(f"Error checking status: {status_response.status_code}")
                    break
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
