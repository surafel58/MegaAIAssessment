"""
WebSocket endpoint: /ws/ingest?session_id={uuid}

Receives raw JPEG frames from the browser, runs face detection,
stores ROI data, and forwards annotated frames to the stream queue.
"""
import json
import re

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.frame_processor import process_frame

router = APIRouter()

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


@router.websocket("/ws/ingest")
async def ws_ingest(
    websocket: WebSocket,
    session_id: str = Query(...),
):
    if not _UUID_RE.match(session_id):
        await websocket.close(code=4000, reason="session_id must be a valid UUID v4")
        return

    await websocket.accept()
    queue_registry: dict = websocket.app.state.queue_registry

    if session_id not in queue_registry:
        import asyncio
        queue_registry[session_id] = asyncio.Queue(maxsize=settings.MAX_QUEUE_SIZE)

    frame_number = 0
    try:
        while True:
            raw = await websocket.receive_bytes()

            if len(raw) > settings.MAX_FRAME_BYTES:
                await websocket.close(code=4001, reason="Frame exceeds 2 MB limit")
                return

            async with AsyncSessionLocal() as db:
                ack = await process_frame(
                    raw_bytes=raw,
                    session_id=session_id,
                    frame_number=frame_number,
                    queue_registry=queue_registry,
                    db=db,
                )
                await db.commit()

            await websocket.send_text(json.dumps(ack))
            frame_number += 1

    except WebSocketDisconnect:
        pass
    finally:
        # Signal stream that this session ended
        q = queue_registry.get(session_id)
        if q is not None:
            try:
                q.put_nowait(None)  # sentinel
            except Exception:
                pass
