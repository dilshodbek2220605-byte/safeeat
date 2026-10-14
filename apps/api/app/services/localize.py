"""Xavf sabablarini uz/ru/en tillariga tarjima qilish.

AI matn yozmaydi — biz kod bo'yicha tayyor tarjima shablonlarini ishlatamiz.
Bu izchillik va xavfsizlikni ta'minlaydi.
"""

from __future__ import annotations

from app.models.enums import Language

# Har bir kod uchun uch tilda shablon. `{ref}` — allergen / E-code / shart nomi.
TEMPLATES: dict[str, dict[str, str]] = {
    "allergy_match": {
        "uz": "⚠️ Sizda {ref} ga allergiya bor — bu mahsulotda mavjud!",
        "ru": "⚠️ У вас аллергия на {ref} — обнаружено в продукте!",
        "en": "⚠️ You are allergic to {ref} — detected in this product!",
    },
    "condition_sugar": {
        "uz": "Shakar miqdori yuqori ({ref} g) — diabet uchun xavfli.",
        "ru": "Высокое содержание сахара ({ref} г) — опасно при диабете.",
        "en": "High sugar content ({ref} g) — risky for diabetes.",
    },
    "condition_sodium": {
        "uz": "Tuz/natriy yuqori ({ref} mg) — gipertoniya uchun tavsiya etilmaydi.",
        "ru": "Много соли/натрия ({ref} мг) — не рекомендуется при гипертонии.",
        "en": "High sodium ({ref} mg) — not recommended for hypertension.",
    },
    "condition_gluten": {
        "uz": "Tarkibida glyuten bor — seliakiya uchun taqiqlangan.",
        "ru": "Содержит глютен — запрещено при целиакии.",
        "en": "Contains gluten — forbidden for celiac disease.",
    },
    "condition_fat": {
        "uz": "To'yingan yog' miqdori yuqori — xolesterin uchun ehtiyot bo'ling.",
        "ru": "Много жиров — будьте осторожны при высоком холестерине.",
        "en": "High fat content — be careful with high cholesterol.",
    },
    "high_calories": {
        "uz": "Kaloriyasi yuqori ({ref} kcal) — kunlik maqsadingizga mos kelmasligi mumkin.",
        "ru": "Высокая калорийность ({ref} ккал) — может не соответствовать вашей цели.",
        "en": "High calorie content ({ref} kcal) — may not fit your daily goal.",
    },
    "high_risk_additive": {
        "uz": "Zararli E-qo'shimcha aniqlandi: {ref}.",
        "ru": "Обнаружена вредная добавка: {ref}.",
        "en": "Harmful additive detected: {ref}.",
    },
    "banned_additive": {
        "uz": "🚫 Taqiqlangan/yuqori xavfli qo'shimcha: {ref}.",
        "ru": "🚫 Запрещённая/высокорискованная добавка: {ref}.",
        "en": "🚫 Banned/high-risk additive: {ref}.",
    },
    "base_risk_moderate": {
        "uz": "Umumiy tarkib me'yorida, lekin me'yorida iste'mol qiling.",
        "ru": "Состав в целом в норме, но употребляйте умеренно.",
        "en": "Composition is generally fine, but consume in moderation.",
    },
    "base_risk_dangerous": {
        "uz": "Mahsulot tarkibi umuman xavfli deb baholandi.",
        "ru": "Состав продукта оценён как опасный.",
        "en": "The product composition was assessed as unsafe.",
    },
    "all_clear": {
        "uz": "✅ Sizning profilingizga mos — xavfsiz iste'mol qilishingiz mumkin.",
        "ru": "✅ Подходит вашему профилю — можно употреблять безопасно.",
        "en": "✅ Matches your profile — safe to consume.",
    },
}

# Allergen va kasallik nomlarining chiroyli ko'rinishi
LABELS: dict[str, dict[str, str]] = {
    "lactose": {"uz": "laktoza", "ru": "лактоза", "en": "lactose"},
    "nuts": {"uz": "yong'oq", "ru": "орехи", "en": "nuts"},
    "gluten": {"uz": "glyuten", "ru": "глютен", "en": "gluten"},
    "peanut": {"uz": "yer yong'og'i", "ru": "арахис", "en": "peanut"},
    "egg": {"uz": "tuxum", "ru": "яйцо", "en": "egg"},
    "soy": {"uz": "soya", "ru": "соя", "en": "soy"},
    "fish": {"uz": "baliq", "ru": "рыба", "en": "fish"},
    "shellfish": {"uz": "dengiz mahsulotlari", "ru": "морепродукты", "en": "shellfish"},
    "sesame": {"uz": "kunjut", "ru": "кунжут", "en": "sesame"},
    "honey": {"uz": "asal", "ru": "мёд", "en": "honey"},
    "diabetes": {"uz": "diabet", "ru": "диабет", "en": "diabetes"},
    "hypertension": {"uz": "gipertoniya", "ru": "гипертония", "en": "hypertension"},
    "celiac": {"uz": "seliakiya", "ru": "целиакия", "en": "celiac disease"},
}


def t(key: str, language: Language | str, **kwargs: object) -> str:
    """Kodni tanlangan tilga tarjima qiladi."""
    lang = language.value if isinstance(language, Language) else language
    if lang not in {"uz", "ru", "en"}:
        lang = "en"
    entry = TEMPLATES.get(key)
    if not entry:
        return key
    template = entry.get(lang, entry["en"])
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template


def label(code: str, language: Language | str) -> str:
    """Allergen/kasallik kodini chiroyli nomga aylantiradi."""
    lang = language.value if isinstance(language, Language) else language
    if lang not in {"uz", "ru", "en"}:
        lang = "en"
    entry = LABELS.get(code)
    if not entry:
        return code
    return entry.get(lang, entry["en"])


# Xavf darajasi yorliqlari (frontendda ham kerak bo'lishi mumkin)
RISK_LABELS: dict[str, dict[str, str]] = {
    "safe": {"uz": "🟢 Xavfsiz", "ru": "🟢 Безопасно", "en": "🟢 Safe"},
    "moderate": {"uz": "🟡 Me'yorda", "ru": "🟡 Умеренно", "en": "🟡 Moderate"},
    "dangerous": {"uz": "🔴 Taqiqlangan", "ru": "🔴 Опасно", "en": "🔴 Dangerous"},
}
