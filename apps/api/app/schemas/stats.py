"""Statistika va kalendar sxemalari."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.models.enums import RiskLevel


class SummaryStats(BaseModel):
    total_analyses: int
    safe_count: int
    moderate_count: int
    dangerous_count: int
    total_calories: float
    avg_calories: float
    analyses_last_7_days: int


class CalendarDay(BaseModel):
    day: date
    total: int
    status: RiskLevel | None = None  # eng yomon holat (kalendar rangi uchun)
    calories: float = 0


class CalendarResponse(BaseModel):
    year: int
    month: int
    days: list[CalendarDay]
