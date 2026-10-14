"""`users` jadvali — foydalanuvchi profili va sozlamalari."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONType, TimestampMixin, UUIDMixin
from app.models.enums import Gender, Goal, Language, Theme


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    # ---- Telegram ----
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    photo_url: Mapped[str | None] = mapped_column(String(512))
    language_code: Mapped[str | None] = mapped_column(String(8))

    # ---- Afzalliklar ----
    language: Mapped[Language] = mapped_column(
        Enum(Language, name="language_enum"), default=Language.uz, nullable=False
    )
    theme: Mapped[Theme] = mapped_column(
        Enum(Theme, name="theme_enum"), default=Theme.system, nullable=False
    )

    # ---- Profil / salomatlik ----
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender_enum"))
    height_cm: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    goal: Mapped[Goal | None] = mapped_column(Enum(Goal, name="goal_enum"))

    # Kasalliklar va allergiyalar — moslashuvchan ro'yxat (masalan ["diabetes", "hypertension"])
    chronic_conditions: Mapped[list[str]] = mapped_column(JSONType, default=list, nullable=False)
    allergies: Mapped[list[str]] = mapped_column(JSONType, default=list, nullable=False)

    daily_calorie_target: Mapped[int | None] = mapped_column(Integer)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # ---- Munosabatlar ----
    analyses: Mapped[list[Analysis]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    daily_summaries: Mapped[list[DailySummary]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} tg={self.telegram_id}>"
