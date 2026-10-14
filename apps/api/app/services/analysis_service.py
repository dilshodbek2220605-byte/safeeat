"""Tahlil pipeline'i — rasm qabul qilishdan tayyor natijagacha.

1. Rasmni qayta ishlash (validatsiya/resize/EXIF strip/hash)
2. Storage'ga saqlash
3. `pending` yozuv yaratish
4. AI Vision (fallback bilan) → `AIResult`
5. Deterministik RiskEngine → shaxsiy xavf
6. `analyses` + `daily_summaries` yangilash
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.analysis import Analysis
from app.models.daily_summary import DailySummary
from app.models.enums import AnalysisStatus, RiskLevel
from app.models.user import User
from app.schemas.ai_result import AIResult
from app.services import image as image_service
from app.services.ai import ProfileContext, analyze_image
from app.services.risk_engine import RiskEngine
from app.services.storage import get_storage

logger = get_logger(__name__)


def _dec(value: float | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


async def run_analysis(
    session: AsyncSession,
    *,
    user: User,
    raw_image: bytes,
    content_type: str,
) -> Analysis:
    """To'liq tahlil oqimini bajaradi va saqlangan `Analysis` ni qaytaradi."""
    # 1) Rasmni qayta ishlash
    processed, mime, image_hash = image_service.process_image(raw_image, content_type)

    # 2) Saqlash
    storage = get_storage()
    image_url = await storage.save(processed, mime_type=mime, user_id=str(user.id))

    # 3) Pending yozuv
    analysis = Analysis(
        user_id=user.id,
        image_url=image_url,
        image_hash=image_hash,
        status=AnalysisStatus.pending,
    )
    session.add(analysis)
    await session.flush()

    # 4) AI Vision
    context = ProfileContext(
        language=user.language.value,
        allergies=user.allergies or [],
        conditions=user.chronic_conditions or [],
        goal=user.goal.value if user.goal else None,
    )
    try:
        vision = await analyze_image(processed, mime, context)
    except Exception as exc:  # noqa: BLE001 — har qanday AI xatosini saqlaymiz
        analysis.status = AnalysisStatus.failed
        analysis.error_message = str(exc)[:1000]
        await session.flush()
        logger.exception("AI tahlil muvaffaqiyatsiz")
        raise

    ai_result: AIResult = vision.result

    # 5) Deterministik xavf
    engine = RiskEngine(
        language=user.language,
        allergies=user.allergies or [],
        conditions=user.chronic_conditions or [],
        goal=user.goal,
    )
    risk = engine.evaluate(ai_result)

    # 6) Natijani yozish
    _apply_result(analysis, ai_result, vision, risk)
    analysis.status = AnalysisStatus.success
    await session.flush()

    # 7) Kunlik jamlanma
    await _update_daily_summary(session, user_id=user.id, analysis=analysis)

    return analysis


def _apply_result(analysis: Analysis, ai: AIResult, vision, risk) -> None:
    analysis.provider = vision.provider
    analysis.food_name = ai.food_name
    analysis.confidence = _dec(ai.confidence)
    analysis.portion_estimate_g = _dec(ai.portion_estimate_g)

    n = ai.nutrition
    analysis.calories = _dec(n.calories)
    analysis.protein_g = _dec(n.protein_g)
    analysis.carbs_g = _dec(n.carbs_g)
    analysis.fat_g = _dec(n.fat_g)
    analysis.fiber_g = _dec(n.fiber_g)
    analysis.sugar_g = _dec(n.sugar_g)
    analysis.sodium_mg = _dec(n.sodium_mg)

    analysis.ingredients = [i.model_dump(mode="json") for i in ai.ingredients]
    analysis.additives = [a.model_dump(mode="json") for a in ai.additives]
    analysis.allergen_matches = ai.allergen_flags

    analysis.risk_level = risk.risk_level
    analysis.risk_score = risk.risk_score
    analysis.risk_reasons = risk.reasons
    analysis.personalized_warning = risk.personalized_warning

    analysis.ai_latency_ms = vision.latency_ms
    analysis.raw_ai_response = vision.raw


async def _update_daily_summary(session: AsyncSession, *, user_id: uuid.UUID, analysis: Analysis) -> None:
    """Bugungi kunlik jamlanmani yangilaydi (upsert)."""
    today = datetime.now().date()
    result = await session.execute(
        select(DailySummary).where(DailySummary.user_id == user_id, DailySummary.day == today)
    )
    summary = result.scalar_one_or_none()
    if summary is None:
        summary = DailySummary(user_id=user_id, day=today, total_calories=Decimal(0))
        session.add(summary)
        await session.flush()

    summary.total_analyses += 1
    if analysis.risk_level == RiskLevel.safe:
        summary.safe_count += 1
    elif analysis.risk_level == RiskLevel.moderate:
        summary.moderate_count += 1
    elif analysis.risk_level == RiskLevel.dangerous:
        summary.dangerous_count += 1

    summary.total_calories = float(summary.total_calories or 0) + float(analysis.calories or 0)
    await session.flush()


async def rebuild_daily_summary(session: AsyncSession, *, user_id: uuid.UUID, day: date) -> None:
    """Kunlik jamlanmani tahlillar asosida qayta hisoblaydi (o'chirishdan keyin)."""
    from sqlalchemy import func

    result = await session.execute(
        select(
            func.count(Analysis.id),
            func.coalesce(func.sum(Analysis.calories), 0),
        ).where(
            Analysis.user_id == user_id,
            func.date(Analysis.created_at) == day,
            Analysis.status == AnalysisStatus.success,
        )
    )
    total, calories = result.one()

    counts = dict.fromkeys(RiskLevel, 0)
    rows = await session.execute(
        select(Analysis.risk_level, func.count(Analysis.id))
        .where(
            Analysis.user_id == user_id,
            func.date(Analysis.created_at) == day,
            Analysis.status == AnalysisStatus.success,
        )
        .group_by(Analysis.risk_level)
    )
    for level, count in rows.all():
        if level is not None:
            counts[level] = count

    result = await session.execute(
        select(DailySummary).where(DailySummary.user_id == user_id, DailySummary.day == day)
    )
    summary = result.scalar_one_or_none()
    if summary is None:
        summary = DailySummary(user_id=user_id, day=day)
        session.add(summary)

    summary.total_analyses = int(total or 0)
    summary.total_calories = float(calories or 0)
    summary.safe_count = counts[RiskLevel.safe]
    summary.moderate_count = counts[RiskLevel.moderate]
    summary.dangerous_count = counts[RiskLevel.dangerous]
    await session.flush()
