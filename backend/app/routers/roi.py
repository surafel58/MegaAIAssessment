"""
REST endpoint: GET /api/roi

Returns paginated ROI detection records for a given session.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db_session
from app.schemas import RoiPageResponse
from app.utils import is_valid_uuid

router = APIRouter(prefix="/api")


@router.get("/roi", response_model=RoiPageResponse)
async def get_roi(
    session_id: Annotated[str, Query(description="Session UUID")],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    from_frame: Annotated[int, Query(ge=0)] = 0,
    to_frame: Annotated[int | None, Query(ge=0)] = None,
    db: AsyncSession = Depends(get_db_session),
) -> RoiPageResponse:
    if not is_valid_uuid(session_id):
        raise HTTPException(status_code=400, detail="session_id must be a valid UUID v4")

    return await crud.get_roi_records(
        db,
        session_id=session_id,
        limit=limit,
        offset=offset,
        from_frame=from_frame,
        to_frame=to_frame,
    )
