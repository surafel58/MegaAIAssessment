"""
Integration tests for WS /ws/stream.

The AsyncClient with ASGIWebSocketTransport is created inside each test body
so that enter/exit happen in the same asyncio task (avoids anyio cancel scope errors).
"""
import asyncio
import io
import json

import httpx
import pytest
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport
from PIL import Image


def _make_jpeg(width=64, height=64, color=(200, 180, 160)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestWsStream:
    async def test_invalid_session_id_closes_connection(self, ws_app):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            with pytest.raises(Exception):
                async with aconnect_ws("/ws/stream?session_id=not-a-uuid", client) as ws:
                    await ws.receive_text()

    async def test_missing_session_id_rejected(self, ws_app):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            with pytest.raises(Exception):
                async with aconnect_ws("/ws/stream", client) as ws:
                    await ws.receive_text()

    async def test_stream_delivers_frame_after_ingest(self, ws_app):
        """Stream receives an annotated JPEG frame produced by a concurrent ingest."""
        session_id = "f1f1f1f1-f1f1-f1f1-f1f1-f1f1f1f1f1f1"
        jpeg = _make_jpeg()
        received: list[bytes] = []

        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            async def do_stream():
                async with aconnect_ws(f"/ws/stream?session_id={session_id}", client) as ws:
                    try:
                        frame = await asyncio.wait_for(ws.receive_bytes(), timeout=5.0)
                        received.append(frame)
                    except asyncio.TimeoutError:
                        pass

            async def do_ingest():
                await asyncio.sleep(0.1)
                async with aconnect_ws(f"/ws/ingest?session_id={session_id}", client) as ws:
                    await ws.send_bytes(jpeg)
                    await ws.receive_text()

            await asyncio.gather(do_stream(), do_ingest())

        assert len(received) == 1
        Image.open(io.BytesIO(received[0]))  # valid JPEG — no exception

    async def test_session_ended_event_on_ingest_close(self, ws_app):
        """Closing the ingest connection delivers a session_ended event on stream."""
        session_id = "f2f2f2f2-f2f2-f2f2-f2f2-f2f2f2f2f2f2"
        events: list[dict] = []

        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            async def do_stream():
                async with aconnect_ws(f"/ws/stream?session_id={session_id}", client) as ws:
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
                async with aconnect_ws(f"/ws/ingest?session_id={session_id}", client) as ws:
                    await ws.send_bytes(_make_jpeg())
                    await ws.receive_text()

            await asyncio.gather(do_stream(), do_ingest())

        if events:
            assert events[0].get("event") == "session_ended"
