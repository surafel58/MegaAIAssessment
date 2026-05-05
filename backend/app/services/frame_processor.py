"""
Orchestrates the per-frame pipeline:
  raw JPEG → detect face → draw bbox → store ROI → push to stream queue
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.detection.detector import detect_face
from app.detection.drawing import draw_bounding_box

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="detector")


async def process_frame(
    raw_bytes: bytes,
    session_id: str,
    frame_number: int,
    queue_registry: dict[str, asyncio.Queue],
    db: AsyncSession,
) -> dict:
    loop = asyncio.get_event_loop()

    result = await loop.run_in_executor(_executor, detect_face, raw_bytes)

    if result.detected and result.bbox is not None:
        bbox = result.bbox
        annotated = await loop.run_in_executor(
            _executor,
            draw_bounding_box,
            raw_bytes,
            bbox.x, bbox.y, bbox.width, bbox.height,
        )
        await crud.insert_roi(
            db,
            session_id=session_id,
            frame_number=frame_number,
            bbox_x=bbox.x,
            bbox_y=bbox.y,
            bbox_width=bbox.width,
            bbox_height=bbox.height,
            confidence=result.confidence,
            frame_width=result.frame_width,
            frame_height=result.frame_height,
        )
        output_bytes = annotated
    else:
        output_bytes = raw_bytes

    queue = queue_registry.get(session_id)
    if queue is not None:
        if queue.full():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
        try:
            queue.put_nowait(output_bytes)
        except asyncio.QueueFull:
            pass

    return {
        "frame": frame_number,
        "detected": result.detected,
        "confidence": result.confidence,
    }
