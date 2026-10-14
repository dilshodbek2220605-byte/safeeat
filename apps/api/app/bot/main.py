"""Bot ishga tushirish nuqtasi.

Ish rejimi:
  * ENV=development  → long-polling (webhook kerak emas, oson)
  * ENV=production   → webhook (WEBHOOK_BASE_URL ishlatiladi)

`python -m app.bot.main` orqali ishga tushiriladi.
"""

from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo

from app.bot.handlers import router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


async def _configure_bot(bot: Bot) -> None:
    settings = get_settings()
    # Menu button — WebApp'ni ochadi
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Open SafeEat",
                web_app=WebAppInfo(url=settings.webapp_url),
            )
        )
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Start"),
                BotCommand(command="help", description="Help"),
            ]
        )
    except Exception as exc:  # noqa: BLE001 — tarmoq/ruxsat xatosi
        logger.warning("Bot menyusini sozlab bo'lmadi: %s", exc)


async def run_polling(bot: Bot, dp: Dispatcher) -> None:
    logger.info("Bot long-polling rejimida ishga tushdi")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def run_webhook(bot: Bot, dp: Dispatcher) -> None:
    """aiohttp orqali webhook serverni ishga tushiradi."""
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web

    settings = get_settings()
    path = f"/bot/webhook/{settings.telegram_webhook_secret}"
    webhook_url = f"{settings.webhook_base_url.rstrip('/')}{path}"

    await bot.set_webhook(
        webhook_url,
        secret_token=settings.telegram_webhook_secret or None,
        drop_pending_updates=True,
    )
    logger.info("Webhook o'rnatildi: %s", webhook_url)

    app = web.Application()
    handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.telegram_webhook_secret or None,
    )
    handler.register(app, path=path)
    setup_application(app, dp, bot=bot)

    async def _health(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    app.router.add_get("/healthz", _health)

    # Render kabi platformalar portni `$PORT` orqali beradi
    port = int(os.environ.get("PORT", "8081"))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)  # noqa: S104 — konteyner ichida tashqi qabul
    await site.start()
    logger.info("Webhook server %s-portda ishlamoqda", port)
    # Cheksiz kutish
    await asyncio.Event().wait()


async def main() -> None:
    setup_logging()
    settings = get_settings()
    if not settings.bot_token:
        raise SystemExit("BOT_TOKEN sozlanmagan — .env faylni to'ldiring")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    await _configure_bot(bot)

    try:
        if settings.is_production:
            await run_webhook(bot, dp)
        else:
            await run_polling(bot, dp)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
