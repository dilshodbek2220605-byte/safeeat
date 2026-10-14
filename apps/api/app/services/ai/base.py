"""AI Vision provayderlari uchun umumiy interfeys."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.ai_result import AIResult


@dataclass
class ProfileContext:
    """AI prompt'ga uzatiladigan foydalanuvchi konteksti (shaxs ma'lumoti emas)."""

    language: str = "uz"
    allergies: list[str] | None = None
    conditions: list[str] | None = None
    goal: str | None = None


@dataclass
class VisionResponse:
    result: AIResult
    provider: str
    latency_ms: int
    raw: dict | None = None


class VisionProvider(ABC):
    """Rasmni tahlil qiluvchi provayder."""

    name: str = "base"

    @abstractmethod
    async def analyze(self, image_bytes: bytes, mime_type: str, context: ProfileContext) -> VisionResponse:
        """Rasmni tahlil qilib, normalizatsiya qilingan `AIResult` qaytaradi."""
