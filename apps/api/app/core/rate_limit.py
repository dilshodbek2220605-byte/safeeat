"""Redis'ga asoslangan sodda sliding-window rate limiter.

Redis mavjud bo'lmasa — fail-open (so'rovni o'tkazib yuboradi), shunda ilova
ishlashda davom etadi. Ishlab chiqarishda Redis mavjudligi tavsiya etiladi.
"""

from __future__ import annotations

import time

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.exceptions import RateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis: Redis | None = None


async def get_redis() -> Redis | None:
    """Lazy — ulanishni bir marta yaratadi."""
    global _redis
    if _redis is not None:
        return _redis
    settings = get_settings()
    try:
        client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await client.ping()
        _redis = client
        return _redis
    except Exception as exc:  # noqa: BLE001 — Redis ixtiyoriy komponent
        logger.warning("Redis mavjud emas, rate-limit o'chirildi: %s", exc)
        return None


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


async def check_rate_limit(key: str, *, limit: int | None = None, window: int | None = None) -> None:
    """`key` bo'yicha `window` soniya ichida `limit` martadan oshmasligini tekshiradi."""
    settings = get_settings()
    limit = limit or settings.rate_limit_analyses_per_hour
    window = window or settings.rate_limit_window_seconds

    client = await get_redis()
    if client is None:
        return  # fail-open

    redis_key = f"rl:{key}"
    now = time.time()
    pipe = client.pipeline()
    pipe.zremrangebyscore(redis_key, 0, now - window)
    pipe.zadd(redis_key, {f"{now}:{id(object())}": now})
    pipe.zcard(redis_key)
    pipe.expire(redis_key, window)
    _, _, count, _ = await pipe.execute()

    if int(count) > limit:
        raise RateLimitError("So'rovlar soni chegaradan oshdi. Birozdan so'ng qayta urinib ko'ring.")


async def mark_once(key: str, *, ttl: int) -> bool:
    """`key`ni `ttl` davomida bir marta belgilaydi.

    Birinchi chaqiruvda True, takroriy chaqiruvda False qaytaradi
    (replay protection uchun).
    """
    client = await get_redis()
    if client is None:
        return True  # Redis yo'q — tekshirib bo'lmaydi
    # SET NX — atomar
    result = await client.set(f"once:{key}", "1", ex=ttl, nx=True)
    return bool(result)
