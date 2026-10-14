"""API integratsiya testlari (aiosqlite + mock AI)."""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient
from PIL import Image

from app.models.enums import RiskLevel
from app.schemas.ai_result import AIResult, Nutrition
from app.services.ai.base import VisionResponse
from tests.conftest import auth_headers, make_init_data

pytestmark = pytest.mark.asyncio


def _jpeg_bytes() -> bytes:
    img = Image.new("RGB", (300, 300), (90, 160, 90))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


async def test_health(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_auth_flow(client: AsyncClient):
    user = {"id": 777, "first_name": "Diyor", "language_code": "ru"}
    resp = await client.post("/api/v1/auth/telegram", json={"initData": make_init_data(user)})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["is_new_user"] is True
    assert body["user"]["language"] == "ru"  # language_code ru → ru

    headers = {"Authorization": f"Bearer {body['tokens']['access_token']}"}
    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["first_name"] == "Diyor"


async def test_auth_rejects_bad_init_data(client: AsyncClient):
    resp = await client.post("/api/v1/auth/telegram", json={"initData": "auth_date=1&hash=deadbeef"})
    assert resp.status_code == 401


async def test_protected_requires_token(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_onboarding_and_profile_update(client: AsyncClient):
    headers = await auth_headers(client, {"id": 888, "first_name": "Ona", "language_code": "uz"})

    onboard = await client.post(
        "/api/v1/users/me/onboarding",
        headers=headers,
        json={
            "language": "uz",
            "age": 35,
            "height_cm": 165,
            "weight_kg": 70,
            "goal": "lose_weight",
            "chronic_conditions": ["diabetes"],
            "allergies": ["Nuts", "nuts", "gluten"],
        },
    )
    assert onboard.status_code == 200, onboard.text
    data = onboard.json()
    assert data["onboarding_completed"] is True
    assert data["allergies"] == ["gluten", "nuts"]  # normalizatsiya + takrorlarni olib tashlash
    assert data["daily_calorie_target"] > 0

    patch = await client.patch(
        "/api/v1/users/me", headers=headers, json={"theme": "dark", "age": 36}
    )
    assert patch.status_code == 200
    assert patch.json()["theme"] == "dark"
    assert patch.json()["age"] == 36


async def test_analyze_flow_with_mock(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    headers = await auth_headers(client, {"id": 999, "first_name": "Aziz", "language_code": "uz"})

    # Onboarding — allergiya bilan
    await client.post(
        "/api/v1/users/me/onboarding",
        headers=headers,
        json={"language": "uz", "allergies": ["nuts"], "chronic_conditions": []},
    )

    # AI'ni mock qilamiz
    async def fake_analyze(image_bytes, mime_type, context):
        result = AIResult(
            food_name="Shokoladli tort",
            confidence=0.92,
            portion_estimate_g=150,
            nutrition=Nutrition(calories=450, protein_g=6, carbs_g=55, fat_g=22, sugar_g=40, sodium_mg=180),
            allergen_flags=["nuts", "gluten"],
            base_risk=RiskLevel.moderate,
        )
        return VisionResponse(result=result, provider="openai", latency_ms=123, raw={"mock": True})

    monkeypatch.setattr("app.services.analysis_service.analyze_image", fake_analyze)

    resp = await client.post(
        "/api/v1/analyses",
        headers=headers,
        files={"image": ("food.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["food_name"] == "Shokoladli tort"
    assert body["risk_level"] == "dangerous"  # nuts allergiyasi
    assert len(body["risk_reasons"]) >= 1

    # Tarixda ko'rinadi
    history = await client.get("/api/v1/analyses", headers=headers)
    assert history.status_code == 200
    assert history.json()["meta"]["total"] == 1

    # Statistika
    summary = await client.get("/api/v1/stats/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["total_analyses"] == 1
    assert summary.json()["dangerous_count"] == 1


async def test_analyze_requires_image(client: AsyncClient):
    headers = await auth_headers(client, {"id": 1010, "first_name": "No", "language_code": "en"})
    resp = await client.post("/api/v1/analyses", headers=headers)
    assert resp.status_code == 422
