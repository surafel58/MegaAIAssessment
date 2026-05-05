from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import ingest, stream, roi


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Per-session queues: session_id -> asyncio.Queue[bytes | None]
    app.state.queue_registry = {}

    # Warm up the detector on the main thread so the first request isn't slow
    from app.detection.detector import _get_detector
    _get_detector()

    yield

    from app.detection.detector import close_all_detectors
    close_all_detectors()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Face Detection API",
        description="Real-time face detection video streaming backend",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ingest.router)
    app.include_router(stream.router)
    app.include_router(roi.router)

    return app


app = create_app()
