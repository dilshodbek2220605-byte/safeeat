"""Tahlil endpointlari: rasm yuklash + AI tahlil, tarix, o'chirish."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, File, Query, UploadFile, status
from sqlalchemy import func, select

from app.core.deps import CurrentUser, SessionDep
from app.core.exceptions import NotFoundError
from app.core.rate_limit import check_rate_limit
from app.models.analysis import Analysis
from app.models.enums import AnalysisStatus, RiskLevel
from app.schemas.analysis import AnalysisRead, NutritionRead, RiskReason
from app.schemas.common import Page, PageMeta
from app.services import analysis_service

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _to_read(a: Analysis) -> AnalysisRead:
    return AnalysisRead(
        id=a.id,
        image_url=a.image_url,
        status=a.status,
        provider=a.provider,
        food_name=a.food_name,
        confidence=float(a.confidence) if a.confidence is not None else None,
        portion_estimate_g=float(a.portion_estimate_g) if a.portion_estimate_g is not None else None,
        nutrition=NutritionRead(
            calories=float(a.calories) if a.calories is not None else None,
            protein_g=float(a.protein_g) if a.protein_g is not None else None,
            carbs_g=float(a.carbs_g) if a.carbs_g is not None else None,
            fat_g=float(a.fat_g) if a.fat_g is not None else None,
            fiber_g=float(a.fiber_g) if a.fiber_g is not None else None,
            sugar_g=float(a.sugar_g) if a.sugar_g is not None else None,
            sodium_mg=float(a.sodium_mg) if a.sodium_mg is not None else None,
        ),
        ingredients=a.ingredients or [],
        additives=a.additives or [],
        allergen_matches=a.allergen_matches or [],
        risk_level=a.risk_level,
        risk_score=a.risk_score,
        risk_reasons=[RiskReason(**r) for r in (a.risk_reasons or [])],
        personalized_warning=a.personalized_warning,
        created_at=a.created_at,
    )


@router.post("", response_model=AnalysisRead, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    user: CurrentUser,
    session: SessionDep,
    image: UploadFile = File(..., description="Taom yoki mahsulot tarkibi rasmi"),
) -> AnalysisRead:
    """Rasmni qabul qiladi, AI Vision tahlil qiladi va natijani saqlaydi."""
    # Suiiste'mol/xarajatni nazorat qilish uchun rate-limit
    await check_rate_limit(f"analyze:{user.id}")

    raw = await image.read()
    content_type = image.content_type or "image/jpeg"

    analysis = await analysis_service.run_analysis(
        session, user=user, raw_image=raw, content_type=content_type
    )
    await session.commit()
    return _to_read(analysis)


@router.get("", response_model=Page[AnalysisRead])
async def list_analyses(
    user: CurrentUser,
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    risk: RiskLevel | None = Query(None, description="Xavf darajasi bo'yicha filtr"),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
) -> Page[AnalysisRead]:
    """Tahlillar tarixi (sahifalangan)."""
    conditions = [Analysis.user_id == user.id, Analysis.status == AnalysisStatus.success]
    if risk is not None:
        conditions.append(Analysis.risk_level == risk)
    if date_from is not None:
        conditions.append(func.date(Analysis.created_at) >= date_from)
    if date_to is not None:
        conditions.append(func.date(Analysis.created_at) <= date_to)

    total = await session.scalar(select(func.count(Analysis.id)).where(*conditions))

    rows = await session.execute(
        select(Analysis)
        .where(*conditions)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = [_to_read(a) for a in rows.scalars().all()]
    return Page(items=items, meta=PageMeta(total=int(total or 0), limit=limit, offset=offset))


@router.get("/{analysis_id}", response_model=AnalysisRead)
async def get_analysis(analysis_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> AnalysisRead:
    analysis = await _get_owned(session, user.id, analysis_id)
    return _to_read(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(analysis_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> None:
    analysis = await _get_owned(session, user.id, analysis_id)
    day = analysis.created_at.date()
    await session.delete(analysis)
    await session.flush()
    # Kunlik jamlanmani qayta hisoblash
    await analysis_service.rebuild_daily_summary(session, user_id=user.id, day=day)
    await session.commit()


async def _get_owned(session, user_id: uuid.UUID, analysis_id: uuid.UUID) -> Analysis:
    result = await session.execute(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise NotFoundError("Tahlil topilmadi")
    return analysis
