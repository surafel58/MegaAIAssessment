"""
Integration tests for GET /api/roi.
"""
import pytest
from httpx import AsyncClient

from app import crud

SESSION_A = "ffffffff-ffff-ffff-ffff-ffffffffffff"


async def _seed(db_session, session_id: str, count: int):
    for i in range(count):
        await crud.insert_roi(
            db_session,
            session_id=session_id,
            frame_number=i,
            bbox_x=10.0,
            bbox_y=20.0,
            bbox_width=100.0,
            bbox_height=120.0,
            confidence=0.95,
            frame_width=640,
            frame_height=480,
        )
    await db_session.commit()


class TestGetRoi:
    async def test_missing_session_id_returns_400(self, client: AsyncClient):
        resp = await client.get("/api/roi")
        assert resp.status_code == 422  # FastAPI treats missing required query param as 422

    async def test_invalid_session_id_returns_400(self, client: AsyncClient):
        resp = await client.get("/api/roi?session_id=not-a-uuid")
        assert resp.status_code == 400

    async def test_empty_session_returns_zero_total(self, client: AsyncClient):
        resp = await client.get("/api/roi?session_id=00000000-0000-0000-0000-000000000099")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_returns_inserted_records(self, client: AsyncClient, db_session):
        sid = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
        await _seed(db_session, sid, 5)
        resp = await client.get(f"/api/roi?session_id={sid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5

    async def test_limit_capped_at_200(self, client: AsyncClient, db_session):
        sid = "dddddddd-dddd-dddd-dddd-dddddddddddd"
        await _seed(db_session, sid, 5)
        resp = await client.get(f"/api/roi?session_id={sid}&limit=9999")
        assert resp.status_code == 422  # limit > 200 fails Pydantic validation

    async def test_response_shape(self, client: AsyncClient, db_session):
        sid = "cccccccc-cccc-0000-cccc-cccccccccccc"
        await _seed(db_session, sid, 1)
        resp = await client.get(f"/api/roi?session_id={sid}")
        item = resp.json()["items"][0]
        assert "id" in item
        assert "frame_number" in item
        assert "timestamp" in item
        assert "bbox" in item
        assert set(item["bbox"].keys()) == {"x", "y", "width", "height"}
        assert "confidence" in item
        assert "frame_width" in item
        assert "frame_height" in item
