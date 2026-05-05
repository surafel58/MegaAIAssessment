"""
Unit tests for detection/detector.py and detection/drawing.py.
These do NOT require a running database or network.
"""
import io

import pytest
from PIL import Image

from app.detection.detector import detect_face, DetectionResult
from app.detection.drawing import draw_bounding_box


class TestDetectFace:
    def test_returns_detection_result_type(self, blank_jpeg):
        result = detect_face(blank_jpeg)
        assert isinstance(result, DetectionResult)

    def test_no_face_in_blank_image(self, blank_jpeg):
        result = detect_face(blank_jpeg)
        assert result.detected is False
        assert result.bbox is None
        assert result.confidence == 0.0

    def test_no_face_in_noise_image(self, noise_jpeg):
        result = detect_face(noise_jpeg)
        assert result.detected is False

    def test_frame_dimensions_populated(self, blank_jpeg):
        result = detect_face(blank_jpeg)
        assert result.frame_width == 100
        assert result.frame_height == 100

    def test_invalid_bytes_returns_no_detection(self):
        result = detect_face(b"not a jpeg at all")
        assert result.detected is False
        assert result.bbox is None

    def test_empty_bytes_returns_no_detection(self):
        result = detect_face(b"")
        assert result.detected is False


class TestDrawBoundingBox:
    def test_output_is_valid_jpeg(self, blank_jpeg):
        out = draw_bounding_box(blank_jpeg, x=10, y=10, width=30, height=30)
        img = Image.open(io.BytesIO(out))
        assert img.format == "JPEG"

    def test_output_dimensions_unchanged(self, blank_jpeg):
        out = draw_bounding_box(blank_jpeg, x=10, y=10, width=30, height=30)
        img = Image.open(io.BytesIO(out))
        assert img.size == (100, 100)

    def test_output_bytes_differ_from_input(self, blank_jpeg):
        """Drawing a visible box must change pixel data."""
        out = draw_bounding_box(blank_jpeg, x=5, y=5, width=40, height=40)
        assert out != blank_jpeg

    def test_full_frame_bbox_does_not_crash(self, blank_jpeg):
        out = draw_bounding_box(blank_jpeg, x=0, y=0, width=100, height=100)
        assert len(out) > 0

    def test_zero_size_bbox(self, blank_jpeg):
        out = draw_bounding_box(blank_jpeg, x=50, y=50, width=0, height=0)
        assert len(out) > 0
