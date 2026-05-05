"""
Face detection using MediaPipe BlazeFace.
No OpenCV (cv2) is used anywhere in this module.
"""
import io
import threading
from dataclasses import dataclass

import mediapipe as mp
import numpy as np
from PIL import Image

from app.config import settings

_local = threading.local()


def _get_detector() -> mp.solutions.face_detection.FaceDetection:
    """Return a thread-local MediaPipe FaceDetection instance."""
    if not hasattr(_local, "detector"):
        _local.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=settings.DETECTION_CONFIDENCE_THRESHOLD,
        )
    return _local.detector


def close_all_detectors() -> None:
    """Called on app shutdown — closes the detector on the calling thread only.
    Worker threads clean up via garbage collection."""
    if hasattr(_local, "detector"):
        _local.detector.close()
        del _local.detector


@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float


@dataclass
class DetectionResult:
    detected: bool
    bbox: BoundingBox | None
    confidence: float
    frame_width: int
    frame_height: int


def detect_face(jpeg_bytes: bytes) -> DetectionResult:
    """
    Detect the first face in a JPEG frame.

    Uses MediaPipe BlazeFace (model_selection=0, short-range).
    Decodes JPEG with Pillow — no cv2 involved.

    Returns a DetectionResult with absolute-pixel bbox coords.
    """
    try:
        img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
        width, height = img.size
        np_img = np.array(img)

        detector = _get_detector()
        results = detector.process(np_img)

        if not results.detections:
            return DetectionResult(
                detected=False, bbox=None, confidence=0.0,
                frame_width=width, frame_height=height,
            )

        det = results.detections[0]
        rb = det.location_data.relative_bounding_box
        confidence = float(det.score[0])

        x = max(0.0, rb.xmin * width)
        y = max(0.0, rb.ymin * height)
        w = min(rb.width * width, width - x)
        h = min(rb.height * height, height - y)

        return DetectionResult(
            detected=True,
            bbox=BoundingBox(x=x, y=y, width=w, height=h),
            confidence=confidence,
            frame_width=width,
            frame_height=height,
        )
    except Exception:
        try:
            img = Image.open(io.BytesIO(jpeg_bytes))
            w, h = img.size
        except Exception:
            w, h = 0, 0
        return DetectionResult(
            detected=False, bbox=None, confidence=0.0,
            frame_width=w, frame_height=h,
        )
