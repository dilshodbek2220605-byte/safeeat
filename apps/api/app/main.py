"""FastAPI ilova kirish nuqtasi.

- Lifespan: logging, static papkani tayyorlash, Redis'ni yopish
- CORS: faqat WebApp originlariga ruxsat
- StaticFiles: lokal saqlangan rasmlarni berish (dev)
- Exception handler'lar: yagona JSON xatolik formati
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import close_redis

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("SafeEat AI API ishga tushdi (env=%s)", settings.env)
    yield
    await close_redis()
    logger.info("SafeEat AI API to'xtadi")


def create_app() -> FastAPI:
    app = FastAPI(
        title="SafeEat AI API",
        description="Telegram Mini App uchun oziq-ovqat va suv xavfsizligi tahlili",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Yagona xatolik formati
    register_exception_handlers(app)

    # API router
    app.include_router(api_router, prefix="/api/v1")

    # Lokal rasmlarni berish (dev / STORAGE_BACKEND=local uchun)
    if settings.storage_backend == "local":
        from pathlib import Path

        storage_dir = Path(settings.local_storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/static/uploads", StaticFiles(directory=str(storage_dir)), name="uploads")

    return app


app = create_app()
