"""Ilova sozlamalari — Pydantic Settings orqali `.env` dan o'qiladi.

Barcha konfiguratsiya bitta joyda, type-safe va validatsiya qilingan holda
saqlanadi. `get_settings()` lru_cache bilan singletona qaytaradi.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Umumiy ----
    env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    webapp_url: str = "http://localhost:5173"
    api_public_url: str = "http://localhost:8000"
    webhook_base_url: str = "http://localhost:8000"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # ---- Database ----
    database_url: str = "postgresql+asyncpg://safeeat:safeeat@localhost:5432/safeeat"
    db_echo: bool = False

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- Telegram ----
    bot_token: str = ""
    telegram_webhook_secret: str = ""

    # ---- JWT ----
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # ---- AI ----
    ai_provider_order: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["openai", "gemini"])
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    ai_timeout_seconds: int = 45
    ai_max_retries: int = 2

    # ---- Storage ----
    storage_backend: Literal["local", "s3"] = "local"
    local_storage_dir: str = "uploads"
    max_upload_mb: int = 10
    s3_endpoint_url: str | None = None
    s3_region: str = "auto"
    s3_bucket: str = "safeeat"
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_public_base_url: str | None = None

    # ---- Rate limit ----
    rate_limit_analyses_per_hour: int = 20
    rate_limit_window_seconds: int = 3600

    # ---- initData ----
    init_data_max_age_seconds: int = 24 * 3600  # 24 soat

    @field_validator("cors_origins", "ai_provider_order", mode="before")
    @classmethod
    def _split_csv(cls, v: object) -> object:
        """`"a,b,c"` ko'rinishidagi env qiymatini listga aylantiradi."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, v: object) -> object:
        """Bulutli provayderlar (Render / Railway / Heroku) beradigan
        `postgres://...` manzilini SQLAlchemy async dialektiga o'giradi.

        - `postgres://` / `postgresql://` → `postgresql+asyncpg://`
        - `sslmode=...` olib tashlanadi (asyncpg uni qabul qilmaydi)
        """
        if not isinstance(v, str):
            return v

        url = v
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                url = f"postgresql+asyncpg://{url[len(prefix):]}"
                break

        parts = urlsplit(url)
        if parts.query:
            query = [(k, val) for k, val in parse_qsl(parts.query) if k != "sslmode"]
            url = urlunsplit(
                (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
            )
        return url

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
