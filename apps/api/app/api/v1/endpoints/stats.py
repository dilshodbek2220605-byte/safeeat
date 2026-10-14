"""Statistika va kalendar endpointlari."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.deps import CurrentUser, SessionDep
from app.schemas.stats import CalendarResponse, SummaryStats
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=SummaryStats)
async def summary(user: CurrentUser, session: SessionDep) -> SummaryStats:
    """Umumiy statistika: jami tahlillar, xavf taqsimoti, kaloriyalar."""
    return await stats_service.get_summary(session, user.id)


@router.get("/calendar", response_model=CalendarResponse)
async def calendar(
    user: CurrentUser,
    session: SessionDep,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
) -> CalendarResponse:
    """Bir oy uchun kunlik salomatlik holati (kalendar uchun)."""
    return await stats_service.get_calendar(session, user.id, year, month)
