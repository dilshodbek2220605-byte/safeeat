"""Foydalanuvchi bilan bog'liq biznes-logika."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Language
from app.models.user import User


async def upsert_from_telegram(session: AsyncSession, tg_user: dict[str, Any]) -> tuple[User, bool]:
    """Telegram `user` obyektidan foydalanuvchini topadi yoki yaratadi.

    Qaytaradi: (user, is_new)
    """
    telegram_id = int(tg_user["id"])
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    is_new = user is None
    if user is None:
        user = User(
            telegram_id=telegram_id,
            language=_map_language(tg_user.get("language_code")),
            language_code=tg_user.get("language_code"),
        )
        session.add(user)

    # Telegram'dan kelgan profil maydonlarini yangilab turamiz
    user.username = tg_user.get("username") or user.username
    user.first_name = tg_user.get("first_name") or user.first_name
    user.last_name = tg_user.get("last_name") or user.last_name
    user.photo_url = tg_user.get("photo_url") or user.photo_url
    user.last_seen_at = datetime.now(UTC)

    await session.flush()
    return user, is_new


def _map_language(code: str | None) -> Language:
    if not code:
        return Language.uz
    code = code.lower()
    if code.startswith("ru"):
        return Language.ru
    if code.startswith("en"):
        return Language.en
    return Language.uz


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def touch_last_seen(session: AsyncSession, user: User) -> None:
    user.last_seen_at = datetime.now(UTC)
    await session.flush()
