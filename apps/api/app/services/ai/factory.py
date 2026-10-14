"""AI provayderlar fabrikasi va fallback orkestratori.

`AI_PROVIDER_ORDER=openai,gemini` bo'yicha ketma-ket urinadi. Asosiy provayder
bir necha marta urinadi; xato bo'lsa keyingisiga o'tadi.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger
from app.services.ai.base import ProfileContext, VisionProvider, VisionResponse

logger = get_logger(__name__)


def _build_provider(name: str) -> VisionProvider:
    # Lokal import — ishlatilmagan provayder bog'liqliklarini yuklamaslik uchun
    if name == "openai":
        from app.services.ai.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if name == "gemini":
        from app.services.ai.gemini_provider import GeminiProvider

        return GeminiProvider()
    raise AIProviderError(f"Noma'lum AI provayder: {name}")


async def analyze_image(image_bytes: bytes, mime_type: str, context: ProfileContext) -> VisionResponse:
    """Provayderlar zanjirini sinab ko'radi va birinchi muvaffaqiyatli natijani qaytaradi."""
    settings = get_settings()
    order = settings.ai_provider_order or ["openai"]
    errors: list[str] = []

    for provider_name in order:
        try:
            provider = _build_provider(provider_name)
        except AIProviderError as exc:
            errors.append(f"{provider_name}: {exc.message}")
            continue

        for attempt in range(1, settings.ai_max_retries + 1):
            try:
                logger.info("AI tahlil: provider=%s urinish=%s", provider_name, attempt)
                return await provider.analyze(image_bytes, mime_type, context)
            except AIProviderError as exc:
                errors.append(f"{provider_name} (urinish {attempt}): {exc.message}")
                logger.warning("Provayder %s xatosi: %s", provider_name, exc.message)

    raise AIProviderError("Barcha AI provayderlar muvaffaqiyatsiz: " + " | ".join(errors[-4:]))
