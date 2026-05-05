"""
WebSocket endpoint: /ws/ingest?session_id={uuid}

Receives raw JPEG frames from the browser, runs face detection,
stores ROI data, and forwards annotated frames to the stream queue.
"""
import asyncio
import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.frame_processor import process_frame
from app.utils import is_valid_uuid

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/ingest")
async def ws_ingest(
    websocket: WebSocket,
    session_id: str = Query(...),
):
    if not is_valid_uuid(session_id):
        await websocket.close(code=4000, reason="session_id must be a valid UUID v4")
        return

    await websocket.accept()
    state = websocket.app.state
    queue_registry: dict[str, asyncio.Queue] = state.queue_registry
    frame_counters: dict[str, int] = state.frame_counters

    queue_registry.setdefault(
        session_id, asyncio.Queue(maxsize=settings.MAX_QUEUE_SIZE)
    )

    try:
        while True:
            try:
                raw = await asyncio.wait_for(
                    websocket.receive_bytes(),
                    timeout=settings.STREAM_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                await websocket.close(code=1001, reason="Ingest timeout — no frames received")
                return

            if len(raw) > settings.MAX_FRAME_BYTES:
                await websocket.close(code=4001, reason="Frame exceeds 2 MB limit")
                return

            frame_number = frame_counters.get(session_id, 0)

            try:
                async with AsyncSessionLocal() as db:
                    ack = await process_frame(
                        raw_bytes=raw,
                        session_id=session_id,
                        frame_number=frame_number,
                        queue_registry=queue_registry,
                        db=db,
                    )
                    await db.commit()
            except Exception:
                logger.exception(
                    "Frame %d processing error for session %s", frame_number, session_id
                )
                ack = {"frame": frame_number, "detected": False, "confidence": 0.0}

            frame_counters[session_id] = frame_number + 1
            await websocket.send_text(json.dumps(ack))

    except WebSocketDisconnect:
        pass
    finally:
        q = queue_registry.get(session_id)
        if q is not None:
            try:
                q.put_nowait(None)  # sentinel — signals stream the session ended
            except Exception:
                pass
