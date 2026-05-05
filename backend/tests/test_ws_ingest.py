"""
Integration tests for WS /ws/ingest using httpx-ws + ASGI transport.

The AsyncClient with ASGIWebSocketTransport is created inside each test body
so that enter/exit happen in the same asyncio task (avoids anyio cancel scope errors).
"""
import json
import io
import pytest
import httpx
from PIL import Image
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport


def _make_jpeg(width=64, height=64, color=(200, 180, 160)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestWsIngest:
    async def test_valid_jpeg_returns_ack(self, ws_app):
        session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            async with aconnect_ws(f"/ws/ingest?session_id={session_id}", client) as ws:
                await ws.send_bytes(_make_jpeg())
                msg = await ws.receive_text()
                ack = json.loads(msg)
                assert "frame" in ack
                assert "detected" in ack
                assert "confidence" in ack
                assert ack["frame"] == 0

    async def test_second_frame_increments_frame_number(self, ws_app):
        session_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            async with aconnect_ws(f"/ws/ingest?session_id={session_id}", client) as ws:
                await ws.send_bytes(_make_jpeg())
                ack1 = json.loads(await ws.receive_text())
                await ws.send_bytes(_make_jpeg())
                ack2 = json.loads(await ws.receive_text())
                assert ack2["frame"] == ack1["frame"] + 1

    async def test_invalid_bytes_returns_ack_gracefully(self, ws_app):
        session_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            async with aconnect_ws(f"/ws/ingest?session_id={session_id}", client) as ws:
                await ws.send_bytes(b"not a jpeg")
                msg = await ws.receive_text()
                ack = json.loads(msg)
                assert "detected" in ack
                assert ack["detected"] is False

    async def test_invalid_session_id_closes_connection(self, ws_app):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            with pytest.raises(Exception):
                async with aconnect_ws("/ws/ingest?session_id=not-a-uuid", client) as ws:
                    await ws.receive_text()

    async def test_missing_session_id_rejected(self, ws_app):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(app=ws_app), base_url="http://testserver"
        ) as client:
            with pytest.raises(Exception):
                async with aconnect_ws("/ws/ingest", client) as ws:
                    await ws.receive_text()
