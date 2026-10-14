"""User / profil sxemalari."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Gender, Goal, Language, Theme

# Profil uchun ruxsat etilgan qiymatlar (frontenddagi chiplar bilan mos)
KNOWN_CONDITIONS = {
    "diabetes",
    "hypertension",
    "celiac",
    "heart_disease",
    "kidney_disease",
    "gout",
    "high_cholesterol",
    "ibs",
}
KNOWN_ALLERGIES = {
    "lactose",
    "nuts",
    "gluten",
    "peanut",
    "egg",
    "soy",
    "fish",
    "shellfish",
    "sesame",
    "honey",
}


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    photo_url: str | None = None

    language: Language
    theme: Theme

    age: int | None = None
    gender: Gender | None = None
    height_cm: int | None = None
    weight_kg: float | None = None
    goal: Goal | None = None

    chronic_conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)

    daily_calorie_target: int | None = None
    onboarding_completed: bool
    created_at: datetime
    last_seen_at: datetime | None = None


class UserUpdate(BaseModel):
    """Profilni qismiy yangilash (barcha maydonlar ixtiyoriy)."""

    language: Language | None = None
    theme: Theme | None = None
    age: int | None = Field(default=None, ge=1, le=120)
    gender: Gender | None = None
    height_cm: int | None = Field(default=None, ge=50, le=250)
    weight_kg: float | None = Field(default=None, ge=20, le=400)
    goal: Goal | None = None
    chronic_conditions: list[str] | None = None
    allergies: list[str] | None = None
    daily_calorie_target: int | None = Field(default=None, ge=500, le=10000)


class OnboardingRequest(BaseModel):
    """Onboarding yakunida to'liq profil to'plami."""

    language: Language
    theme: Theme = Theme.system
    age: int | None = Field(default=None, ge=1, le=120)
    gender: Gender | None = None
    height_cm: int | None = Field(default=None, ge=50, le=250)
    weight_kg: float | None = Field(default=None, ge=20, le=400)
    goal: Goal | None = None
    chronic_conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
