from datetime import datetime
from pydantic import BaseModel


class BboxSchema(BaseModel):
    x: float
    y: float
    width: float
    height: float


class RoiItem(BaseModel):
    id: str
    frame_number: int
    timestamp: datetime
    bbox: BboxSchema
    confidence: float
    frame_width: int
    frame_height: int

    model_config = {"from_attributes": True}


class RoiPageResponse(BaseModel):
    session_id: str
    total: int
    has_next: bool
    items: list[RoiItem]


class WsAck(BaseModel):
    frame: int
    detected: bool
    confidence: float
