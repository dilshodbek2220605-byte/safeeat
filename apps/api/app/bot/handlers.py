"""Bot handlerlari: /start va yordam."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.bot.keyboards import main_menu_keyboard
from app.core.logging import get_logger

router = Router(name="main")
logger = get_logger(__name__)

_WELCOME = {
    "uz": (
        "👋 *SafeEat AI* ga xush kelibsiz!\n\n"
        "Taom yoki mahsulot tarkibini suratga oling — AI tarkibni tahlil qilib, "
        "sizning allergiya va kasalliklaringizga mos kelishini aytadi.\n\n"
        "Tugmani bosing va boshlang 👇"
    ),
    "ru": (
        "👋 Добро пожаловать в *SafeEat AI*!\n\n"
        "Сфотографируйте еду или состав продукта — ИИ проанализирует состав и "
        "скажет, подходит ли он вам с учётом аллергий и заболеваний.\n\n"
        "Нажмите кнопку ниже 👇"
    ),
    "en": (
        "👋 Welcome to *SafeEat AI*!\n\n"
        "Take a photo of your meal or ingredient list — the AI analyzes the "
        "composition and checks it against your allergies and conditions.\n\n"
        "Tap the button below to start 👇"
    ),
}


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    lang = (message.from_user.language_code or "uz")[:2] if message.from_user else "uz"
    text = _WELCOME.get(lang, _WELCOME["en"])
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Buyruqlar:\n/start — botni ishga tushirish\n/help — yordam",
        reply_markup=main_menu_keyboard(),
    )


@router.message()
async def fallback(message: Message) -> None:
    """Boshqa xabarlarga bir xil javob (WebApp tugmasi bilan)."""
    await message.answer(
        "Ilovani ochish uchun quyidagi tugmani bosing 👇",
        reply_markup=main_menu_keyboard(),
    )
