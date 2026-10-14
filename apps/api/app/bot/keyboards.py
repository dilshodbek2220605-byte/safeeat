"""aiogram bot uchun klaviaturalar."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import get_settings


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """WebApp'ni ochuvchi asosiy tugma."""
    settings = get_settings()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍎 SafeEat AI'ni ochish",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ],
        ]
    )
