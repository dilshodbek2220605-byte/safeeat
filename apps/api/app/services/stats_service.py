"""Statistika va kalendar uchun yordamchi so'rovlar."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.daily_summary import DailySummary
from app.models.enums import AnalysisStatus, RiskLevel
from app.schemas.stats import CalendarDay, CalendarResponse, SummaryStats


async def get_summary(session: AsyncSession, user_id: uuid.UUID) -> SummaryStats:
    base_where = (Analysis.user_id == user_id, Analysis.status == AnalysisStatus.success)

    totals = await session.execute(
        select(
            func.count(Analysis.id),
            func.coalesce(func.sum(Analysis.calories), 0),
            func.coalesce(func.avg(Analysis.calories), 0),
        ).where(*base_where)
    )
    total, total_calories, avg_calories = totals.one()

    counts = dict.fromkeys(RiskLevel, 0)
    rows = await session.execute(
        select(Analysis.risk_level, func.count(Analysis.id)).where(*base_where).group_by(Analysis.risk_level)
    )
    for level, count in rows.all():
        if level is not None:
            counts[level] = count

    week_ago = date.today() - timedelta(days=7)
    last7 = await session.execute(
        select(func.count(Analysis.id)).where(
            *base_where,
            func.date(Analysis.created_at) >= week_ago,
        )
    )

    return SummaryStats(
        total_analyses=int(total or 0),
        safe_count=counts[RiskLevel.safe],
        moderate_count=counts[RiskLevel.moderate],
        dangerous_count=counts[RiskLevel.dangerous],
        total_calories=float(total_calories or 0),
        avg_calories=round(float(avg_calories or 0), 1),
        analyses_last_7_days=int(last7.scalar_one() or 0),
    )


_STATUS_RANK = {RiskLevel.safe: 0, RiskLevel.moderate: 1, RiskLevel.dangerous: 2, None: -1}


async def get_calendar(session: AsyncSession, user_id: uuid.UUID, year: int, month: int) -> CalendarResponse:
    """Bir oy uchun kunlik holat (kalendar uchun)."""
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    rows = await session.execute(
        select(DailySummary).where(
            DailySummary.user_id == user_id,
            DailySummary.day >= start,
            DailySummary.day < end,
        )
    )
    summaries = {s.day: s for s in rows.scalars().all()}

    days: list[CalendarDay] = []
    cursor = start
    while cursor < end:
        s = summaries.get(cursor)
        worst: RiskLevel | None = None
        if s and s.total_analyses > 0:
            candidates = []
            if s.dangerous_count:
                candidates.append(RiskLevel.dangerous)
            if s.moderate_count:
                candidates.append(RiskLevel.moderate)
            if s.safe_count:
                candidates.append(RiskLevel.safe)
            worst = max(candidates, key=lambda lvl: _STATUS_RANK[lvl]) if candidates else None

        days.append(
            CalendarDay(
                day=cursor,
                total=int(s.total_analyses) if s else 0,
                status=worst,
                calories=float(s.total_calories) if s else 0,
            )
        )
        cursor += timedelta(days=1)

    return CalendarResponse(year=year, month=month, days=days)
