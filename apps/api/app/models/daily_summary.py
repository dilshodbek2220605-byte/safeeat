"""`daily_summaries` — kalendar uchun kunlik jamlanma (materializatsiya)."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import GUID, Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class DailySummary(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "daily_summaries"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    day: Mapped[date] = mapped_column(Date, nullable=False)

    total_analyses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    safe_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    moderate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dangerous_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_calories: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    user: Mapped[User] = relationship(back_populates="daily_summaries")

    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_daily_summaries_user_day"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DailySummary user={self.user_id} day={self.day}>"
