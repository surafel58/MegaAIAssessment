# Real-Time Face Detection Video Streaming System

A containerised full-stack app that captures webcam video, detects faces in real time, draws bounding boxes, stores detection data in PostgreSQL, and streams the annotated feed back to the browser.

## Architecture

![System Architecture](architecture/system_diagram.png)

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite → nginx |
| Backend | Python 3.12 + FastAPI + uvicorn |
| Face Detection | MediaPipe BlazeFace (`mp.solutions.face_detection`) |
| Bounding Box Drawing | Pillow `ImageDraw.rectangle()` |
| Database | PostgreSQL 16 + SQLAlchemy (async) + Alembic |
| Containerisation | Docker Compose |

> **No OpenCV (`cv2`) is used anywhere.** JPEG frames are decoded with Pillow and passed to MediaPipe as NumPy arrays.

---

## Quick Start

**Prerequisites:** Docker Desktop (includes Compose v2), Git

```bash
git clone <repo-url>
cd MegaAIAssessment
cp .env.example .env          # defaults work out of the box
docker compose up --build
```

First build downloads Python 3.12, MediaPipe (~200 MB), and Node.js; allow ~4–5 minutes.

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API (Swagger UI) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 (see `.env`) |

Click **Start** in the browser, allow camera access, and your face will be detected and annotated in real time.

---

## API Endpoints

### `WS /ws/ingest?session_id={uuid}`
Receives raw JPEG frames (binary) from the browser at up to 15 fps.  
Returns a JSON ack per frame: `{"frame": 42, "detected": true, "confidence": 0.97}`

### `WS /ws/stream?session_id={uuid}`
Streams annotated JPEG frames (binary) back to the browser.  
On session end: `{"event": "session_ended"}`

### `GET /api/roi`
Returns paginated ROI detection records from the database.

| Query Param | Default | Description |
|---|---|---|
| `session_id` | required | UUID of the session |
| `limit` | 50 | Max records (≤ 200) |
| `offset` | 0 | Pagination offset |
| `from_frame` | 0 | Start frame number (inclusive) |
| `to_frame` | — | End frame number (inclusive) |

**Response:**
```json
{
  "session_id": "uuid",
  "total": 142,
  "items": [{
    "id": "uuid",
    "frame_number": 47,
    "timestamp": "2026-05-05T14:23:01.123Z",
    "bbox": { "x": 210.5, "y": 88.0, "width": 134.2, "height": 148.7 },
    "confidence": 0.9873,
    "frame_width": 640,
    "frame_height": 480
  }]
}
```

---

## Running Tests

```bash
docker compose exec backend pytest tests/ -v
```

Or locally (requires Python 3.12 and `pip install -r requirements.txt`):

```bash
cd backend
pytest tests/ -v
```

Tests use an in-memory SQLite database so no Postgres instance is needed.

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── detection/      # MediaPipe detector + Pillow drawing
│   │   ├── routers/        # WS ingest, WS stream, REST /api/roi
│   │   ├── services/       # frame_processor orchestrator
│   │   ├── main.py         # FastAPI app factory
│   │   ├── models.py       # SQLAlchemy ORM
│   │   ├── crud.py         # DB helpers
│   │   └── schemas.py      # Pydantic I/O types
│   ├── alembic/            # DB migrations
│   ├── tests/              # pytest suite
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── hooks/          # useWebcamCapture, useVideoStream
│   │   ├── components/     # VideoDisplay, RoiTable, StatusBar
│   │   └── api/            # REST client
│   ├── nginx.conf
│   └── Dockerfile
├── db/
│   └── init.sql            # Schema + indexes
├── architecture/
│   └── system_diagram.png
└── docker-compose.yml
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `libGL.so.1: cannot open shared object file` | MediaPipe's internal cv2 needs OpenGL | Add `libgl1` to the Dockerfile apt-get line and rebuild |
| `relation "roi_detections" already exists` | Alembic ran against a DB already initialised by `init.sql` | Run `docker compose down -v` to wipe the volume, then `docker compose up` |
| `column "id" is of type uuid but expression is of type character varying` | `init.sql` used `UUID` type but ORM uses `String(36)` | Run `docker compose down -v` to reset, then bring up with the corrected `init.sql` |
| Frontend blank / "camera not found" | Browser blocked camera for non-HTTPS origin | Use `localhost` (not an IP), or set `chrome://flags/#unsafely-treat-insecure-origin-as-secure` |
| `pg_isready` healthcheck fails | Wrong DB name in healthcheck | Ensure healthcheck uses `-d ${POSTGRES_DB}` not a hard-coded name |
| Backend crashes on startup with `ModuleNotFoundError` | Python 3.13 does not have mediapipe wheels | Pin `python:3.12-slim` in the Dockerfile |

---

## Design Decisions

### Why MediaPipe over OpenCV?
The constraint prohibits `cv2`. MediaPipe's `mp.solutions.face_detection` runs BlazeFace internally and accepts NumPy arrays in RGB format — no OpenCV dependency at any point in the pipeline.

### Why Pillow for drawing?
`ImageDraw.rectangle()` provides axis-aligned bounding box drawing with a single line. No external library needed beyond what is already used for JPEG decode/encode.

### Why two WebSocket connections?
Separating ingest (`/ws/ingest`) and stream (`/ws/stream`) lets each side reconnect independently. An `asyncio.Queue(maxsize=2)` bridges them with automatic backpressure — the oldest frame is dropped when the queue is full, keeping latency minimal.

### Why SQLAlchemy async + Alembic?
Async sessions avoid blocking the event loop during DB writes (which happen on every detected frame). Alembic ensures the schema is always current on startup (`alembic upgrade head` in the Docker CMD).

---

## Security Notes

- Frame size limited to 2 MB; oversized frames close the WebSocket (code 4001)
- `session_id` validated as UUID v4 regex before any DB interaction
- CORS configured via `BACKEND_CORS_ORIGINS` env var — no wildcard `*` in production
- All DB credentials in `.env` (gitignored); `.env.example` committed with placeholders
- All package versions pinned in `requirements.txt`

---

## AI Collaboration Attestation

This project was built with AI assistance (Claude Code by Anthropic).

**AI was used for:**
- Architecture planning and technology selection
- Writing boilerplate (Alembic env.py, FastAPI lifespan, React hook scaffolding)
- Test structure and fixtures

**All code was reviewed and verified by the developer.** Critical design decisions — face detection library choice, no-OpenCV constraint adherence, async DB session management, WebSocket backpressure approach — were validated by reading the generated code and understanding each decision.
