from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RoiDetection
from app.schemas import RoiItem, RoiPageResponse, BboxSchema


async def insert_roi(
    db: AsyncSession,
    session_id: str,
    frame_number: int,
    bbox_x: float,
    bbox_y: float,
    bbox_width: float,
    bbox_height: float,
    confidence: float,
    frame_width: int,
    frame_height: int,
) -> str:
    record = RoiDetection(
        session_id=session_id,
        frame_number=frame_number,
        bbox_x=bbox_x,
        bbox_y=bbox_y,
        bbox_width=bbox_width,
        bbox_height=bbox_height,
        confidence=confidence,
        frame_width=frame_width,
        frame_height=frame_height,
    )
    db.add(record)
    await db.flush()
    return record.id


async def get_roi_records(
    db: AsyncSession,
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    from_frame: int = 0,
    to_frame: int | None = None,
) -> RoiPageResponse:
    base_q = select(RoiDetection).where(
        RoiDetection.session_id == session_id,
        RoiDetection.frame_number >= from_frame,
    )
    if to_frame is not None:
        base_q = base_q.where(RoiDetection.frame_number <= to_frame)

    count_q = select(func.count()).select_from(base_q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    rows_q = base_q.order_by(RoiDetection.timestamp.desc()).limit(limit).offset(offset)
    rows = (await db.execute(rows_q)).scalars().all()

    items = [
        RoiItem(
            id=r.id,
            frame_number=r.frame_number,
            timestamp=r.timestamp,
            bbox=BboxSchema(x=r.bbox_x, y=r.bbox_y, width=r.bbox_width, height=r.bbox_height),
            confidence=r.confidence,
            frame_width=r.frame_width,
            frame_height=r.frame_height,
        )
        for r in rows
    ]

    return RoiPageResponse(
        session_id=session_id,
        total=total,
        has_next=(offset + len(items) < total),
        items=items,
    )
