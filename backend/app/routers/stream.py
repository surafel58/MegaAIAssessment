"""
WebSocket endpoint: /ws/stream?session_id={uuid}

Streams annotated JPEG frames to the browser.
Frames are sourced from a per-session asyncio.Queue populated by the ingest router.
"""
import asyncio
import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.config import settings
from app.utils import is_valid_uuid

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/stream")
async def ws_stream(
    websocket: WebSocket,
    session_id: str = Query(...),
):
    if not is_valid_uuid(session_id):
        await websocket.close(code=4000, reason="session_id must be a valid UUID v4")
        return

    await websocket.accept()
    queue_registry: dict[str, asyncio.Queue] = websocket.app.state.queue_registry

    queue_registry.setdefault(
        session_id, asyncio.Queue(maxsize=settings.MAX_QUEUE_SIZE)
    )
    queue: asyncio.Queue = queue_registry[session_id]

    try:
        while True:
            frame_bytes = await asyncio.wait_for(
                queue.get(), timeout=settings.STREAM_TIMEOUT_SECONDS
            )

            if frame_bytes is None:
                await websocket.send_text(json.dumps({"event": "session_ended"}))
                await websocket.close()
                break

            await websocket.send_bytes(frame_bytes)

    except asyncio.TimeoutError:
        logger.debug("Stream timeout for session %s", session_id)
        await websocket.send_text(json.dumps({"event": "timeout"}))
        await websocket.close()
    except WebSocketDisconnect:
        pass
    finally:
        queue_registry.pop(session_id, None)
