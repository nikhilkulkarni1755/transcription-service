# Video Transcription Service

A lightweight microservice system that transcribes YouTube videos using AI. Simply provide a YouTube URL and get back the full transcription - no video files are stored, everything is streamed and processed on-the-fly.

## Features

- **Zero-storage streaming** - Audio is streamed directly without saving files to disk
- **Smart caching** - Never transcribe the same video twice (stored in database)
- **Bandwidth efficient** - Only downloads audio stream, not video pixels
- **Async processing** - Submit videos and check status later
- **Docker-based** - Easy deployment with docker-compose
- **AI-powered** - Uses Whisper model via HuggingFace Transformers (100% free)

## Architecture

The service consists of two Docker containers:

1. **API Service** (Port 8000) - FastAPI application managing requests and database
2. **Transcriber Service** (Port 8002) - Streams audio and runs Whisper transcription model

## Quick Start

### Prerequisites

- Docker and Docker Compose
- That's it! (Python 3.13+ and uv only needed for local development)

### Setup and Run

```bash
# Clone the repository
git clone <your-repo-url>
cd video-transcription-service

# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`

### Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove orphan containers
docker-compose down --remove-orphans
```

## API Usage

### 1. Submit a Video for Transcription

```bash
POST http://localhost:8000/api/v1/transcribe
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Example (PowerShell):**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transcribe" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Example (curl):**

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Response:**

```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "status": "pending",
  "transcription_text": null,
  "error_message": null,
  "created_at": "2025-12-05T10:00:00",
  "updated_at": "2025-12-05T10:00:00"
}
```

### 2. Check Transcription Status

```bash
GET http://localhost:8000/api/v1/transcription/{video_url}
```

**Example:**

```bash
# URL must be encoded
curl "http://localhost:8000/api/v1/transcription/https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ"
```

**Response (when completed):**

```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "status": "completed",
  "transcription_text": "The full transcription text...",
  "error_message": null,
  "created_at": "2025-12-05T10:00:00",
  "updated_at": "2025-12-05T10:05:00"
}
```

### 3. Health Check

```bash
GET http://localhost:8000/health
```

## Status States

| Status         | Description                                     |
| -------------- | ----------------------------------------------- |
| `pending`      | Request submitted, waiting to start             |
| `transcribing` | Streaming audio and running transcription model |
| `completed`    | Transcription finished successfully             |
| `failed`       | An error occurred (check `error_message` field) |

## Project Structure

```
video-transcription-service/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic models
│   ├── models/
│   │   └── transcription.py   # SQLAlchemy models
│   ├── services/
│   │   └── transcription_service.py  # Transcriber client
│   ├── database.py            # Database setup
│   └── main.py                # FastAPI app
├── docker/
│   └── transcriber/
│       ├── app.py             # Streaming + Whisper transcription
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Local Development

If you want to run the API locally (not in Docker):

```bash
# Install dependencies
python -m uv sync

# Run the API service
uv run uvicorn app.main:app --reload --port 8000
```

**Note:** You'll still need the transcriber service running in Docker for this to work.

## Technologies Used

- **FastAPI** - Modern web framework for building APIs
- **uv** - Fast Python package manager
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Database for caching transcriptions
- **HuggingFace Transformers** - Whisper model for transcription
- **yt-dlp** - YouTube audio streaming
- **Docker** - Containerization

## Configuration

Environment variables can be set in `docker-compose.yml`:

- `TRANSCRIBER_URL` - URL of the transcriber service (default: `http://transcriber:8002`)

## Important Notes

- The Whisper-base model will be downloaded on first run (~140 MB)
- **No video or audio files are stored** - everything is streamed and processed in memory
- Only audio is downloaded from videos, saving significant bandwidth
- The database (`transcriptions.db`) only stores transcription text, not media files
- For production, consider using PostgreSQL instead of SQLite
- For better transcription quality, modify the transcriber to use `openai/whisper-large-v3` (still free via HuggingFace)

## Troubleshooting

### YouTube 403 Forbidden Errors

If you get 403 errors when transcribing:

1. Make sure you're using the latest yt-dlp version (rebuild with `--no-cache`)
2. Some videos have stricter protections - try different videos
3. YouTube may temporarily block your IP - wait and try again later

### Check Logs

```bash
# View API logs
docker-compose logs api --tail 50

# View transcriber logs
docker-compose logs transcriber --tail 50

# Follow logs in real-time
docker-compose logs -f
```

## License

MIT

## Attempt

This is an attempt to build the fastest transcription machine in the world. looking to use streaming to try and get a less that 5 second completion time for shorter vids.
