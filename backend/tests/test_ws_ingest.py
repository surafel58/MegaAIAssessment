"""
Integration tests for WS /ws/ingest using httpx + ASGI transport.
"""
import json
import io
import pytest
from PIL import Image
from httpx import AsyncClient


def _make_jpeg(width=64, height=64, color=(200, 180, 160)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestWsIngest:
    async def test_valid_jpeg_returns_ack(self, client: AsyncClient):
        session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        async with client.websocket_connect(f"/ws/ingest?session_id={session_id}") as ws:
            await ws.send_bytes(_make_jpeg())
            msg = await ws.receive_text()
            ack = json.loads(msg)
            assert "frame" in ack
            assert "detected" in ack
            assert "confidence" in ack
            assert ack["frame"] == 0

    async def test_second_frame_increments_frame_number(self, client: AsyncClient):
        session_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        async with client.websocket_connect(f"/ws/ingest?session_id={session_id}") as ws:
            await ws.send_bytes(_make_jpeg())
            ack1 = json.loads(await ws.receive_text())
            await ws.send_bytes(_make_jpeg())
            ack2 = json.loads(await ws.receive_text())
            assert ack2["frame"] == ack1["frame"] + 1

    async def test_invalid_bytes_returns_ack_gracefully(self, client: AsyncClient):
        session_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        async with client.websocket_connect(f"/ws/ingest?session_id={session_id}") as ws:
            await ws.send_bytes(b"not a jpeg")
            msg = await ws.receive_text()
            ack = json.loads(msg)
            assert "detected" in ack
            assert ack["detected"] is False

    async def test_invalid_session_id_closes_connection(self, client: AsyncClient):
        with pytest.raises(Exception):
            async with client.websocket_connect("/ws/ingest?session_id=not-a-uuid") as ws:
                await ws.receive_text()

    async def test_missing_session_id_rejected(self, client: AsyncClient):
        with pytest.raises(Exception):
            async with client.websocket_connect("/ws/ingest") as ws:
                await ws.receive_text()
