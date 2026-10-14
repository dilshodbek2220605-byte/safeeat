"""Pytest konfiguratsiyasi va umumiy fixture'lar.

Testlar SQLite (aiosqlite) xotirada ishlaydi — shu sababli haqiqiy PostgreSQL
kerak emas. Modellar portativ turlar (JSONType/GUID) ishlatadi.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from collections.abc import AsyncGenerator
from urllib.parse import urlencode

# `app` import qilinishidan OLDIN env o'rnatilishi kerak
os.environ.setdefault("BOT_TOKEN", "123456:TEST_BOT_TOKEN_ABC")
os.environ.setdefault("JWT_SECRET", "test-secret-key-please-change-to-32bytes")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("STORAGE_BACKEND", "local")
os.environ.setdefault("LOCAL_STORAGE_DIR", "test_uploads")
os.environ.setdefault("AI_PROVIDER_ORDER", "openai")
os.environ.setdefault("ENV", "development")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402

TEST_BOT_TOKEN = os.environ["BOT_TOKEN"]


def make_init_data(user: dict, *, bot_token: str = TEST_BOT_TOKEN, auth_date: int | None = None) -> str:
    """Haqiqiy Telegram initData'ni generatsiya qiladi (HMAC bilan)."""
    data = {
        "auth_date": str(auth_date if auth_date is not None else int(time.time())),
        "query_id": "AAF_test_query_id",
        "user": json.dumps(user, separators=(",", ":"), ensure_ascii=False),
    }
    data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    data["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(data)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()


async def auth_headers(client: AsyncClient, user: dict | None = None) -> dict[str, str]:
    """Yordamchi: initData bilan auth qilib, Authorization sarlavhasini qaytaradi."""
    tg_user = user or {"id": 111222333, "first_name": "Test", "language_code": "uz"}
    resp = await client.post("/api/v1/auth/telegram", json={"initData": make_init_data(tg_user)})
    assert resp.status_code == 200, resp.text
    token = resp.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
