"""AI prompt parse va AIResult validatsiya testlari."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.enums import RiskLevel
from app.schemas.ai_result import AIResult
from app.services.ai.prompts import parse_json_response


def test_parse_plain_json():
    parsed = parse_json_response('{"food_name": "Olma", "confidence": 0.9}')
    assert parsed["food_name"] == "Olma"


def test_parse_markdown_fenced_json():
    text = '```json\n{"food_name": "Banan"}\n```'
    assert parse_json_response(text)["food_name"] == "Banan"


def test_parse_json_with_surrounding_text():
    text = 'Here is the result: {"food_name": "Guruch"} thanks'
    assert parse_json_response(text)["food_name"] == "Guruch"


def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        parse_json_response("bu JSON emas")


def test_ai_result_defaults():
    result = AIResult(food_name="Suv")
    assert result.nutrition.calories == 0
    assert result.base_risk == RiskLevel.safe
    assert result.ingredients == []


def test_ai_result_normalizes_allergens():
    result = AIResult(food_name="X", allergen_flags=["Nuts", " nuts ", "GLUTEN"])
    assert result.allergen_flags == ["gluten", "nuts"]


def test_ai_result_normalizes_e_code():
    result = AIResult(food_name="X", ingredients=[{"name": "Rang", "e_code": "621"}])
    assert result.ingredients[0].e_code == "E621"


def test_ai_result_requires_food_name():
    with pytest.raises(ValidationError):
        AIResult(food_name="")
