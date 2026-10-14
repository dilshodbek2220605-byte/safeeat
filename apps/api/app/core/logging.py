"""Structured logging sozlamalari (JSON yoki oddiy matn)."""

from __future__ import annotations

import logging
import sys

from app.core.config import get_settings


def ensure_utf8_console() -> None:
    """Windows konsoli (cp1251/cp1252) emoji va kirill matnni buzdmasligi uchun
    stdout/stderr'ni UTF-8 ga o'tkazadi. Boshqa platformalarda xavfsiz no-op."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):  # pragma: no cover — ba'zi muhitlarda yopiq oqim
            pass


def setup_logging() -> None:
    ensure_utf8_console()
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Ba'zi shovqinli loggerlarni bostirish
    for noisy in ("uvicorn.access", "botocore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING if settings.is_production else level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
