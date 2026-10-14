"""Xavfsizlik: Telegram WebApp initData validatsiyasi va JWT.

Telegram `initData` validatsiyasi algoritmi (rasmiy hujjat):
  secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
  data_check_string = "\\n".join(sorted("key=value"))  # hash maydonidan tashqari
  expected_hash = HMAC_SHA256(key=secret_key, msg=data_check_string).hex()
  valid <-> hmac.compare_digest(expected_hash, hash)

Qo'shimcha: `auth_date` yangiligini tekshirish (replay hujumidan himoya).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qsl

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings


class InitDataError(HTTPException):
    """initData validatsiyasidan o'tmagan holatlar uchun."""

    def __init__(self, detail: str = "Invalid Telegram initData") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _build_data_check_string(data: dict[str, str]) -> str:
    """hash maydonini olib tashlab, kalitlar bo'yicha tartiblangan satr qaytaradi."""
    filtered = {k: v for k, v in data.items() if k != "hash" and v is not None}
    return "\n".join(f"{k}={filtered[k]}" for k in sorted(filtered))


def verify_init_data(init_data: str, *, bot_token: str | None = None, max_age: int | None = None) -> dict[str, Any]:
    """`initData` satrini tekshiradi va parsed ma'lumotlarni qaytaradi.

    Xatolarda `InitDataError` (HTTP 401) ko'tariladi.
    """
    settings = get_settings()
    token = bot_token or settings.bot_token
    max_age = max_age if max_age is not None else settings.init_data_max_age_seconds

    if not token:
        raise InitDataError("Server bot token sozlanmagan")
    if not init_data:
        raise InitDataError("initData bo'sh")

    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError as exc:  # noto'g'ri query-string
        raise InitDataError("initData formati noto'g'ri") from exc

    received_hash = parsed.get("hash")
    if not received_hash:
        raise InitDataError("initData ichida 'hash' yo'q")

    data_check_string = _build_data_check_string(parsed)
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # Barlik (timing attack) hujumidan himoyalangan taqqoslash
    if not hmac.compare_digest(expected_hash, received_hash):
        raise InitDataError("initData hash mos kelmadi")

    # Yngilik tekshiruvi
    auth_date_raw = parsed.get("auth_date")
    if auth_date_raw is not None:
        try:
            auth_date = int(auth_date_raw)
        except ValueError as exc:
            raise InitDataError("auth_date noto'g'ri") from exc
        if max_age and time.time() - auth_date > max_age:
            raise InitDataError("initData muddati o'tgan")

    # user maydoni JSON satr sifatida keladi
    user_raw = parsed.get("user")
    if user_raw:
        try:
            parsed["user"] = json.loads(user_raw)
        except json.JSONDecodeError as exc:
            raise InitDataError("initData ichidagi 'user' JSON emas") from exc

    return parsed


# --------------------------------------------------------------------------- #
#                                   JWT                                        #
# --------------------------------------------------------------------------- #

_SENTINEL = object()


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | int) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.refresh_token_expire_days)).timestamp()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """JWT ni dekodlaydi; xato bo'lsa HTTP 401 ko'taradi."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token muddati o'tgan") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token yaroqsiz") from exc
