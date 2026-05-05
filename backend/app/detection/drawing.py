"""
Bounding-box drawing using Pillow only — no OpenCV (cv2) used.
"""
import io

from PIL import Image, ImageDraw

from app.config import settings


def draw_bounding_box(
    jpeg_bytes: bytes,
    x: float,
    y: float,
    width: float,
    height: float,
    color: str = "#00FF41",
    line_width: int = 3,
) -> bytes:
    """
    Draw an axis-aligned rectangular ROI on a JPEG frame.

    Opens the image with Pillow, draws the rectangle, and returns
    the re-encoded JPEG bytes. No cv2 calls anywhere.
    """
    img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    x0, y0 = int(x), int(y)
    x1, y1 = int(x + width), int(y + height)

    draw.rectangle([(x0, y0), (x1, y1)], outline=color, width=line_width)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=settings.JPEG_QUALITY)
    return buf.getvalue()
