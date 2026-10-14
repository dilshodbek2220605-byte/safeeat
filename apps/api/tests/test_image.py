"""Rasm qayta ishlash testlari."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from app.services.image import InvalidImageError, process_image


def _png_bytes(size=(64, 64)) -> bytes:
    img = Image.new("RGB", size, (200, 40, 40))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def test_process_png_ok():
    raw = _png_bytes()
    processed, mime, image_hash = process_image(raw, "image/png")
    assert processed
    assert mime in ("image/png", "image/jpeg")
    assert len(image_hash) == 64


def test_reject_non_image():
    with pytest.raises(InvalidImageError):
        process_image(b"not an image", "image/png")


def test_reject_unsupported_mime():
    with pytest.raises(InvalidImageError):
        process_image(_png_bytes(), "application/pdf")


def test_downscale_large_image():
    raw_big = _png_bytes((2400, 1800))
    processed, mime, _ = process_image(raw_big, "image/png")
    out = Image.open(io.BytesIO(processed))
    assert max(out.size) <= 1280


def test_exif_orientation_stripped():
    # EXIF'siz rasm — oddiy holat ishlashini tekshirish
    raw = _png_bytes((100, 50))
    processed, _, _ = process_image(raw, "image/png")
    out = Image.open(io.BytesIO(processed))
    assert out.size == (100, 50)
