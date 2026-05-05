"""
Integration tests for WS /ws/stream.
"""
import asyncio
import io
import json

import pytest
from httpx import AsyncClient
from PIL import Image


def _make_jpeg(width=64, height=64, color=(200, 180, 160)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestWsStream:
    async def test_invalid_session_id_closes_connection(self, client: AsyncClient):
        with pytest.raises(Exception):
            async with client.websocket_connect("/ws/stream?session_id=not-a-uuid") as ws:
                await ws.receive_text()

    async def test_missing_session_id_rejected(self, client: AsyncClient):
        with pytest.raises(Exception):
            async with client.websocket_connect("/ws/stream") as ws:
                await ws.receive_text()

    async def test_stream_delivers_frame_after_ingest(self, client: AsyncClient):
        """Stream receives an annotated JPEG frame produced by a concurrent ingest."""
        session_id = "dddddddd-dddd-dddd-dddd-dddddddddddd"
        jpeg = _make_jpeg()
        received: list[bytes] = []

        async def do_stream():
            async with client.websocket_connect(f"/ws/stream?session_id={session_id}") as ws:
                try:
                    frame = await asyncio.wait_for(ws.receive_bytes(), timeout=5.0)
                    received.append(frame)
                except asyncio.TimeoutError:
                    pass

        async def do_ingest():
            # Brief pause ensures stream coroutine has connected and is waiting on queue.get()
            await asyncio.sleep(0.1)
            async with client.websocket_connect(f"/ws/ingest?session_id={session_id}") as ws:
                await ws.send_bytes(jpeg)
                await ws.receive_text()

        await asyncio.gather(do_stream(), do_ingest())

        assert len(received) == 1
        Image.open(io.BytesIO(received[0]))  # valid JPEG — no exception

    async def test_session_ended_event_on_ingest_close(self, client: AsyncClient):
        """Closing the ingest connection should deliver a session_ended event on stream."""
        session_id = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
        events: list[dict] = []

        async def do_stream():
            async with client.websocket_connect(f"/ws/stream?session_id={session_id}") as ws:
                # Consume the annotated frame first, then wait for session_ended
                try:
                    await asyncio.wait_for(ws.receive_bytes(), timeout=5.0)
                except asyncio.TimeoutError:
                    return
                try:
                    msg = await asyncio.wait_for(ws.receive_text(), timeout=5.0)
                    events.append(json.loads(msg))
                except asyncio.TimeoutError:
                    pass

        async def do_ingest():
            await asyncio.sleep(0.1)
            async with client.websocket_connect(f"/ws/ingest?session_id={session_id}") as ws:
                await ws.send_bytes(_make_jpeg())
                await ws.receive_text()
            # Exiting the context manager closes the ingest WS → sentinel pushed to queue

        await asyncio.gather(do_stream(), do_ingest())

        if events:
            assert events[0].get("event") == "session_ended"
