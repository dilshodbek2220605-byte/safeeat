"""`additives_catalog` — E-qo'shimchalar ma'lumotnomasi (seed bilan to'ldiriladi)."""

from __future__ import annotations

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import RiskLevel


class Additive(Base):
    __tablename__ = "additives_catalog"

    e_code: Mapped[str] = mapped_column(String(16), primary_key=True)  # masalan "E621"
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str | None] = mapped_column(String(128))
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level_enum"), default=RiskLevel.safe, nullable=False
    )
    description_uz: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Additive {self.e_code} {self.name}>"
