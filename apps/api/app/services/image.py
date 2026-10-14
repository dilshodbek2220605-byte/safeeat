"""Rasm qayta ishlash: validatsiya, EXIF tozalash, resize, hash.

Pillow ishlatiladi. Barcha CPU-bound amallar `run_in_threadpool` orqali
chaqirilishi kerak (endpoint'larda shunday qilinadi).
"""

from __future__ import annotations

import hashlib
import io

from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.core.exceptions import AppError

ALLOWED_MIME = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}
MAX_DIMENSION = 1280


class InvalidImageError(AppError):
    status_code = 400
    code = "invalid_image"


def process_image(raw: bytes, content_type: str) -> tuple[bytes, str, str]:
    """Rasmni tekshiradi va optimallashtiradi.

    Qaytaradi: (tozalangan_bytes, mime_type, sha256_hash)
    EXIF (jumladan GPS) ma'lumotlari olib tashlanadi — maxfiylik uchun.
    """
    settings = get_settings()

    if content_type.lower() not in ALLOWED_MIME:
        raise InvalidImageError(f"Qo'llab-quvvatlanmaydigan format: {content_type}")
    if len(raw) > settings.max_upload_bytes:
        raise InvalidImageError(f"Rasm hajmi {settings.max_upload_mb} MB dan oshmasligi kerak")
    if not raw:
        raise InvalidImageError("Bo'sh fayl")

    image_hash = hashlib.sha256(raw).hexdigest()

    try:
        # `verify()` dan keyin rasmni qayta ochish kerak (fayl pointeri siljiydi)
        probe = Image.open(io.BytesIO(raw))
        probe.verify()
        img = Image.open(io.BytesIO(raw))
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("Rasmni o'qib bo'lmadi yoki fayl buzilgan") from exc

    # EXIF-ni olib tashlash + RGB konvertatsiya (JPEG uchun)
    img = _strip_and_convert(img)

    # Proporsional kichraytirish
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    out = io.BytesIO()
    out_format = "JPEG" if content_type.lower() == "image/webp" else ALLOWED_MIME[content_type.lower()]
    save_kwargs: dict = {"optimize": True}
    if out_format == "JPEG":
        save_kwargs.update({"quality": 85, "progressive": True})
    img.save(out, out_format, **save_kwargs)

    mime = "image/jpeg" if out_format == "JPEG" else f"image/{out_format.lower()}"
    return out.getvalue(), mime, image_hash


def _strip_and_convert(img: Image.Image) -> Image.Image:
    """EXIF/orientation'ni qo'llab, alpha kanalni oq fonga tekislaydi."""
    # Orientation bo'yicha aylantirish, so'ng EXIF yo'qoladi (yangi obyekt)
    try:
        from PIL import ImageOps

        img = ImageOps.exif_transpose(img)
    except Exception:  # noqa: BLE001, S110 — EXIF bo'lmasa shart emas, xavfsiz e'tiborsiz qoldiramiz
        pass

    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        rgba = img.convert("RGBA")
        background.paste(rgba, mask=rgba.split()[-1])
        return background
    if img.mode != "RGB":
        return img.convert("RGB")
    return img
