"""Ma'lumotnoma endpointlari (E-qo'shimchalar katalogi)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.deps import SessionDep
from app.models.additive import Additive

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/additives")
async def list_additives(
    session: SessionDep,
    q: str | None = Query(None, description="Kod yoki nom bo'yicha qidiruv"),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    stmt = select(Additive)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(Additive.e_code.ilike(like) | Additive.name.ilike(like))
    stmt = stmt.limit(limit).order_by(Additive.e_code)
    rows = await session.execute(stmt)
    return [
        {
            "e_code": a.e_code,
            "name": a.name,
            "category": a.category,
            "risk_level": a.risk_level.value,
            "description": {
                "uz": a.description_uz,
                "ru": a.description_ru,
                "en": a.description_en,
            },
        }
        for a in rows.scalars().all()
    ]
