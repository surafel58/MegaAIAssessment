import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import ingest, stream, roi


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.queue_registry: dict[str, asyncio.Queue] = {}
    app.state.frame_counters: dict[str, int] = {}

    from app.detection.detector import _get_detector
    _get_detector()

    yield

    from app.detection.detector import close_all_detectors
    close_all_detectors()

    from app.services.frame_processor import _executor
    _executor.shutdown(wait=False)


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
