"""Barcha enum'lar (Python + PostgreSQL)."""

from __future__ import annotations

import enum


class Language(enum.StrEnum):
    uz = "uz"
    ru = "ru"
    en = "en"


class Gender(enum.StrEnum):
    male = "male"
    female = "female"
    other = "other"


class Goal(enum.StrEnum):
    lose_weight = "lose_weight"
    maintain = "maintain"
    gain_weight = "gain_weight"
    health = "health"


class Theme(enum.StrEnum):
    system = "system"
    light = "light"
    dark = "dark"


class RiskLevel(enum.StrEnum):
    safe = "safe"          # 🟢 Xavfsiz
    moderate = "moderate"  # 🟡 Me'yorda
    dangerous = "dangerous"  # 🔴 Taqiqlangan


class AnalysisStatus(enum.StrEnum):
    pending = "pending"
    success = "success"
    failed = "failed"


class AIProvider(enum.StrEnum):
    openai = "openai"
    gemini = "gemini"
