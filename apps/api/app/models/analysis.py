"""`analyses` jadvali — AI tahlil natijalari tarixi."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import GUID, Base, JSONType, TimestampMixin, UUIDMixin
from app.models.enums import AIProvider, AnalysisStatus, RiskLevel

if TYPE_CHECKING:
    from app.models.user import User


class Analysis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "analyses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # ---- Rasm ----
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    image_hash: Mapped[str | None] = mapped_column(String(64), index=True)

    # ---- AI meta ----
    provider: Mapped[AIProvider | None] = mapped_column(Enum(AIProvider, name="ai_provider_enum"))
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, name="analysis_status_enum"),
        default=AnalysisStatus.pending,
        nullable=False,
    )
    food_name: Mapped[str | None] = mapped_column(String(256))
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))

    # ---- Ozuqaviy qiymat ----
    portion_estimate_g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    calories: Mapped[float | None] = mapped_column(Numeric(8, 2))
    protein_g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    carbs_g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    fat_g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    fiber_g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    sugar_g: Mapped[float | None] = mapped_column(Numeric(7, 2))
    sodium_mg: Mapped[float | None] = mapped_column(Numeric(8, 2))

    # ---- Tarkib / qo'shimchalar ----
    ingredients: Mapped[list | None] = mapped_column(JSONType)
    additives: Mapped[list | None] = mapped_column(JSONType)
    allergen_matches: Mapped[list | None] = mapped_column(JSONType)

    # ---- Shaxsiy xavf bahosi ----
    risk_level: Mapped[RiskLevel | None] = mapped_column(Enum(RiskLevel, name="risk_level_enum"))
    risk_score: Mapped[int | None] = mapped_column(Integer)
    risk_reasons: Mapped[list | None] = mapped_column(JSONType)
    personalized_warning: Mapped[str | None] = mapped_column(Text)

    # ---- Debug / monitoring ----
    raw_ai_response: Mapped[dict | None] = mapped_column(JSONType)
    ai_latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="analyses")

    __table_args__ = (
        Index("ix_analyses_user_created", "user_id", "created_at"),
        Index("ix_analyses_risk", "user_id", "risk_level"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Analysis id={self.id} food={self.food_name} risk={self.risk_level}>"
