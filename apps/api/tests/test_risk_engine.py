"""RiskEngine — deterministik xavf hisoblash testlari."""

from __future__ import annotations

from app.models.enums import Goal, Language, RiskLevel
from app.schemas.ai_result import AdditiveItem, AIResult, IngredientItem, Nutrition
from app.services.risk_engine import RiskEngine


def _result(**overrides) -> AIResult:
    base = {
        "food_name": "Test taom",
        "confidence": 0.9,
        "portion_estimate_g": 200,
        "nutrition": Nutrition(calories=300, protein_g=10, carbs_g=30, fat_g=8, fiber_g=3, sugar_g=5, sodium_mg=200),
        "ingredients": [],
        "allergen_flags": [],
        "additives": [],
        "base_risk": RiskLevel.safe,
    }
    base.update(overrides)
    return AIResult(**base)


def test_allergy_match_is_dangerous():
    engine = RiskEngine(language=Language.uz, allergies=["nuts"], conditions=[])
    ai = _result(allergen_flags=["nuts"])
    result = engine.evaluate(ai)
    assert result.risk_level == RiskLevel.dangerous
    assert any(r["code"] == "allergy_match" for r in result.reasons)
    assert "yong'oq" in result.personalized_warning.lower()


def test_diabetes_high_sugar():
    engine = RiskEngine(language=Language.ru, allergies=[], conditions=["diabetes"])
    ai = _result(nutrition=Nutrition(calories=200, sugar_g=40))
    result = engine.evaluate(ai)
    assert any(r["code"] == "condition_sugar" for r in result.reasons)
    assert result.risk_level in (RiskLevel.moderate, RiskLevel.dangerous)


def test_celiac_gluten_ingredient():
    engine = RiskEngine(language=Language.en, allergies=[], conditions=["celiac"])
    ai = _result(ingredients=[IngredientItem(name="Wheat flour")])
    result = engine.evaluate(ai)
    assert any(r["code"] == "condition_gluten" for r in result.reasons)
    assert result.risk_level == RiskLevel.dangerous


def test_banned_additive():
    engine = RiskEngine(language=Language.uz, allergies=[], conditions=[])
    ai = _result(additives=[AdditiveItem(e_code="E250", name="Sodium nitrite", risk=RiskLevel.dangerous)])
    result = engine.evaluate(ai)
    assert any(r["code"] == "banned_additive" for r in result.reasons)
    assert result.risk_level == RiskLevel.dangerous


def test_safe_food():
    engine = RiskEngine(language=Language.en, allergies=[], conditions=[])
    ai = _result()
    result = engine.evaluate(ai)
    assert result.risk_level == RiskLevel.safe
    assert "safe" in result.personalized_warning.lower() or "✅" in result.personalized_warning


def test_hypertension_sodium():
    engine = RiskEngine(language=Language.uz, allergies=[], conditions=["hypertension"])
    ai = _result(nutrition=Nutrition(calories=250, sodium_mg=1200))
    result = engine.evaluate(ai)
    assert any(r["code"] == "condition_sodium" for r in result.reasons)


def test_high_calories_goal_lose_weight():
    engine = RiskEngine(language=Language.uz, allergies=[], conditions=[], goal=Goal.lose_weight)
    ai = _result(nutrition=Nutrition(calories=700))
    result = engine.evaluate(ai)
    assert any(r["code"] == "high_calories" for r in result.reasons)
