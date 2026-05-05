"""
WebSocket endpoint: /ws/stream?session_id={uuid}

Streams annotated JPEG frames to the browser.
Frames are sourced from a per-session asyncio.Queue populated by the ingest router.
"""
import asyncio
import json
import re

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.config import settings

router = APIRouter()

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


@router.websocket("/ws/stream")
async def ws_stream(
    websocket: WebSocket,
    session_id: str = Query(...),
):
    if not _UUID_RE.match(session_id):
        await websocket.close(code=4000, reason="session_id must be a valid UUID v4")
        return

    await websocket.accept()
    queue_registry: dict = websocket.app.state.queue_registry

    if session_id not in queue_registry:
        queue_registry[session_id] = asyncio.Queue(maxsize=settings.MAX_QUEUE_SIZE)

    queue: asyncio.Queue = queue_registry[session_id]

    try:
        while True:
            frame_bytes = await asyncio.wait_for(queue.get(), timeout=30.0)

            if frame_bytes is None:
                # Ingest session ended
                await websocket.send_text(json.dumps({"event": "session_ended"}))
                await websocket.close()
                break

            await websocket.send_bytes(frame_bytes)

    except asyncio.TimeoutError:
        await websocket.send_text(json.dumps({"event": "timeout"}))
        await websocket.close()
    except WebSocketDisconnect:
        pass
    finally:
        queue_registry.pop(session_id, None)
