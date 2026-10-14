"""Rasm saqlash — adapter pattern (local disk yoki S3-mos object storage).

`.env` dagi `STORAGE_BACKEND` orqali tanlanadi. Kodning qolgan qismi faqat
`StorageBackend` interfeysi bilan ishlaydi — shu sababli dev'da local,
prod'da S3 bo'lishi shaffof.
"""

from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging import get_logger

logger = get_logger(__name__)

_EXT_BY_MIME = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class StorageBackend(ABC):
    """Barcha storage backendlari uchun interfeys."""

    @abstractmethod
    async def save(self, data: bytes, *, mime_type: str, user_id: str | None = None) -> str:
        """Faylni saqlaydi va ochiq (yoki yuklab olinadigan) URL qaytaradi."""

    async def delete(self, url: str) -> None:  # pragma: no cover — ixtiyoriy
        return None


class LocalStorage(StorageBackend):
    """Fayl tizimiga saqlash (dev uchun). FastAPI StaticFiles orqali beriladi."""

    def __init__(self, base_dir: str, public_prefix: str = "/static/uploads") -> None:
        self.base_path = Path(base_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.public_prefix = public_prefix

    async def save(self, data: bytes, *, mime_type: str, user_id: str | None = None) -> str:
        ext = _EXT_BY_MIME.get(mime_type, "jpg")
        rel = f"{user_id or 'anon'}/{uuid.uuid4().hex}.{ext}"
        target = self.base_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)

        def _write() -> None:
            target.write_bytes(data)

        try:
            await asyncio.to_thread(_write)
        except OSError as exc:
            raise StorageError("Faylni diskka yozib bo'lmadi") from exc

        settings = get_settings()
        return f"{settings.api_public_url}{self.public_prefix}/{rel}"


class S3Storage(StorageBackend):
    """S3-mos (AWS S3 / Cloudflare R2 / MinIO / Supabase Storage)."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.s3_bucket:
            raise StorageError("S3 bucket sozlanmagan")
        try:
            import boto3  # lokal import — SDK faqat kerak bo'lganda
        except ImportError as exc:  # pragma: no cover
            raise StorageError("boto3 o'rnatilmagan") from exc

        self._settings = settings
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url or None,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )

    async def save(self, data: bytes, *, mime_type: str, user_id: str | None = None) -> str:
        ext = _EXT_BY_MIME.get(mime_type, "jpg")
        key = f"{user_id or 'anon'}/{uuid.uuid4().hex}.{ext}"

        def _upload() -> None:
            self._client.put_object(
                Bucket=self._settings.s3_bucket,
                Key=key,
                Body=data,
                ContentType=mime_type,
                CacheControl="public, max-age=31536000, immutable",
            )

        try:
            await asyncio.to_thread(_upload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("S3 upload xatosi")
            raise StorageError("Rasmni S3 ga yuklab bo'lmadi") from exc

        if self._settings.s3_public_base_url:
            return f"{self._settings.s3_public_base_url.rstrip('/')}/{key}"
        base = self._settings.s3_endpoint_url or f"https://s3.{self._settings.s3_region}.amazonaws.com"
        return f"{base.rstrip('/')}/{self._settings.s3_bucket}/{key}"


_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Singleton storage backend."""
    global _storage
    if _storage is not None:
        return _storage

    settings = get_settings()
    if settings.storage_backend == "s3":
        _storage = S3Storage()
    else:
        _storage = LocalStorage(settings.local_storage_dir)
    logger.info("Storage backend: %s", settings.storage_backend)
    return _storage
