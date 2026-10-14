"""OpenAI GPT-4o Vision provayderi (chat/completions, JSON mode)."""

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


class OpenAIProvider(VisionProvider):
    name = "openai"

    def __init__(self) -> None:
        self._settings = get_settings()

    async def analyze(self, image_bytes: bytes, mime_type: str, context: ProfileContext) -> VisionResponse:
        if not self._settings.openai_api_key:
            raise AIProviderError("OpenAI API kaliti sozlanmagan")

        b64 = base64.b64encode(image_bytes).decode()
        payload = {
            "model": self._settings.openai_model,
            "temperature": 0.2,
            "max_tokens": 1500,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": build_user_text(context)},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}", "detail": "high"},
                        },
                    ],
                },
            ],
        }

        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self._settings.ai_timeout_seconds) as client:
                resp = await client.post(
                    f"{self._settings.openai_base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {self._settings.openai_api_key}"},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            logger.warning("OpenAI HTTP %s: %s", exc.response.status_code, exc.response.text[:300])
            raise AIProviderError(f"OpenAI xatosi: {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError(f"OpenAI tarmoq xatosi: {exc}") from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        content = data["choices"][0]["message"]["content"]
        try:
            parsed = parse_json_response(content)
            result = AIResult.model_validate(parsed)
        except (ValueError, KeyError) as exc:
            raise AIProviderError(f"OpenAI javobini o'qib bo'lmadi: {exc}") from exc

        return VisionResponse(result=result, provider=self.name, latency_ms=latency_ms, raw=data)
