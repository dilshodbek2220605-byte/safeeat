"""AI Vision natijasining QAT'IY shartnomasi.

Bu model AI dan keladigan JSON'ni validatsiya qiladi. AI faqat FAKTLARNI
qaytaradi; shaxsiy xulosa (risk) `risk_engine` da hisoblanadi.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import RiskLevel


class Nutrition(BaseModel):
    """100% — bitta porsiya (yoki ko'rsatilgan porsiya) uchun ozuqa qiymati."""

    model_config = ConfigDict(extra="ignore")

    calories: float = Field(default=0, ge=0, le=10000)
    protein_g: float = Field(default=0, ge=0, le=1000)
    carbs_g: float = Field(default=0, ge=0, le=2000)
    fat_g: float = Field(default=0, ge=0, le=1000)
    fiber_g: float = Field(default=0, ge=0, le=500)
    sugar_g: float = Field(default=0, ge=0, le=1000)
    sodium_mg: float = Field(default=0, ge=0, le=100000)


class IngredientItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=128)
    is_additive: bool = False
    e_code: str | None = Field(default=None, max_length=16)
    risk: RiskLevel = RiskLevel.safe
    note: str | None = Field(default=None, max_length=500)

    @field_validator("e_code")
    @classmethod
    def _normalize_e_code(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper().replace(" ", "")
        if v and not v.startswith("E"):
            v = f"E{v}"
        return v or None


class AdditiveItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    e_code: str | None = Field(default=None, max_length=16)
    name: str = Field(min_length=1, max_length=200)
    risk: RiskLevel = RiskLevel.safe


class Barcode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    value: str | None = Field(default=None, max_length=64)
    product_name: str | None = Field(default=None, max_length=256)


class AIResult(BaseModel):
    """AI Vision'dan qaytadigan normalizatsiya qilingan natija."""

    model_config = ConfigDict(extra="ignore")

    food_name: str = Field(min_length=1, max_length=256)
    confidence: float = Field(default=0.5, ge=0, le=1)
    portion_estimate_g: float = Field(default=0, ge=0, le=20000)
    nutrition: Nutrition = Field(default_factory=Nutrition)
    ingredients: list[IngredientItem] = Field(default_factory=list)
    allergen_flags: list[str] = Field(default_factory=list)
    additives: list[AdditiveItem] = Field(default_factory=list)
    base_risk: RiskLevel = RiskLevel.safe
    barcode: Barcode | None = None

    @field_validator("allergen_flags")
    @classmethod
    def _normalize_allergens(cls, v: list[str]) -> list[str]:
        return sorted({item.strip().lower() for item in v if item and item.strip()})
