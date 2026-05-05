"""
Unit tests for crud.py against an in-memory SQLite database.
"""
import pytest

from app import crud


SESSION_ID = "11111111-1111-1111-1111-111111111111"


async def _insert(db, frame_number=0, confidence=0.9):
    return await crud.insert_roi(
        db,
        session_id=SESSION_ID,
        frame_number=frame_number,
        bbox_x=10.0,
        bbox_y=20.0,
        bbox_width=100.0,
        bbox_height=120.0,
        confidence=confidence,
        frame_width=640,
        frame_height=480,
    )


class TestInsertRoi:
    async def test_returns_string_id(self, db_session):
        rid = await _insert(db_session)
        await db_session.commit()
        assert isinstance(rid, str)
        assert len(rid) == 36  # UUID v4

    async def test_multiple_inserts_unique_ids(self, db_session):
        id1 = await _insert(db_session, frame_number=1)
        id2 = await _insert(db_session, frame_number=2)
        await db_session.commit()
        assert id1 != id2


class TestGetRoiRecords:
    async def test_empty_session_returns_zero_total(self, db_session):
        page = await crud.get_roi_records(db_session, session_id="00000000-0000-0000-0000-000000000000")
        assert page.total == 0
        assert page.items == []

    async def test_returns_inserted_records(self, db_session):
        sid = "22222222-2222-2222-2222-222222222222"
        for i in range(3):
            await crud.insert_roi(
                db_session, session_id=sid, frame_number=i,
                bbox_x=0, bbox_y=0, bbox_width=10, bbox_height=10,
                confidence=0.8, frame_width=640, frame_height=480,
            )
        await db_session.commit()
        page = await crud.get_roi_records(db_session, session_id=sid)
        assert page.total == 3
        assert len(page.items) == 3

    async def test_limit_respected(self, db_session):
        sid = "33333333-3333-3333-3333-333333333333"
        for i in range(10):
            await crud.insert_roi(
                db_session, session_id=sid, frame_number=i,
                bbox_x=0, bbox_y=0, bbox_width=10, bbox_height=10,
                confidence=0.8, frame_width=640, frame_height=480,
            )
        await db_session.commit()
        page = await crud.get_roi_records(db_session, session_id=sid, limit=3)
        assert len(page.items) == 3
        assert page.total == 10

    async def test_from_frame_filter(self, db_session):
        sid = "44444444-4444-4444-4444-444444444444"
        for i in range(5):
            await crud.insert_roi(
                db_session, session_id=sid, frame_number=i,
                bbox_x=0, bbox_y=0, bbox_width=10, bbox_height=10,
                confidence=0.8, frame_width=640, frame_height=480,
            )
        await db_session.commit()
        page = await crud.get_roi_records(db_session, session_id=sid, from_frame=3)
        assert page.total == 2
        for item in page.items:
            assert item.frame_number >= 3

    async def test_to_frame_filter(self, db_session):
        sid = "55555555-5555-5555-5555-555555555555"
        for i in range(5):
            await crud.insert_roi(
                db_session, session_id=sid, frame_number=i,
                bbox_x=0, bbox_y=0, bbox_width=10, bbox_height=10,
                confidence=0.8, frame_width=640, frame_height=480,
            )
        await db_session.commit()
        page = await crud.get_roi_records(db_session, session_id=sid, to_frame=2)
        assert page.total == 3
        for item in page.items:
            assert item.frame_number <= 2
