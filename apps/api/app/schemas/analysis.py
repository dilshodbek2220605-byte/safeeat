"""Tahlil (analysis) sxemalari."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AIProvider, AnalysisStatus, RiskLevel
from app.schemas.ai_result import AdditiveItem, IngredientItem


class RiskReason(BaseModel):
    code: str          # masalan "allergy_match", "banned_additive"
    severity: RiskLevel
    message: str       # lokalizatsiya qilingan matn
    ref: str | None = None  # qaysi allergen/E-code


class NutritionRead(BaseModel):
    calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image_url: str
    status: AnalysisStatus
    provider: AIProvider | None = None
    food_name: str | None = None
    confidence: float | None = None
    portion_estimate_g: float | None = None

    nutrition: NutritionRead
    ingredients: list[IngredientItem] = Field(default_factory=list)
    additives: list[AdditiveItem] = Field(default_factory=list)
    allergen_matches: list[str] = Field(default_factory=list)

    risk_level: RiskLevel | None = None
    risk_score: int | None = None
    risk_reasons: list[RiskReason] = Field(default_factory=list)
    personalized_warning: str | None = None

    created_at: datetime
