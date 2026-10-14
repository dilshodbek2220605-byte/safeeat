"""Google Gemini 1.5 Flash Vision provayderi (generateContent REST)."""

from __future__ import annotations

import base64
import time

import httpx

from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger
from app.schemas.ai_result import AIResult
from app.services.ai.base import ProfileContext, VisionProvider, VisionResponse
from app.services.ai.prompts import SYSTEM_PROMPT, build_user_text, parse_json_response

logger = get_logger(__name__)

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(VisionProvider):
    name = "gemini"

    def __init__(self) -> None:
        self._settings = get_settings()

    async def analyze(self, image_bytes: bytes, mime_type: str, context: ProfileContext) -> VisionResponse:
        if not self._settings.gemini_api_key:
            raise AIProviderError("Gemini API kaliti sozlanmagan")

        b64 = base64.b64encode(image_bytes).decode()
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": build_user_text(context)},
                        {"inline_data": {"mime_type": mime_type, "data": b64}},
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1500,
                "responseMimeType": "application/json",
            },
        }

        url = f"{GEMINI_BASE}/models/{self._settings.gemini_model}:generateContent"
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self._settings.ai_timeout_seconds) as client:
                resp = await client.post(
                    url,
                    params={"key": self._settings.gemini_api_key},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            logger.warning("Gemini HTTP %s: %s", exc.response.status_code, exc.response.text[:300])
            raise AIProviderError(f"Gemini xatosi: {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError(f"Gemini tarmoq xatosi: {exc}") from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = parse_json_response(content)
            result = AIResult.model_validate(parsed)
        except (KeyError, IndexError, ValueError) as exc:
            raise AIProviderError(f"Gemini javobini o'qib bo'lmadi: {exc}") from exc

        return VisionResponse(result=result, provider=self.name, latency_ms=latency_ms, raw=data)
