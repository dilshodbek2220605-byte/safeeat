"""Boshlang'ich jadvallar: users, analyses, daily_summaries, additives_catalog

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ---- Enum turlari (bir marta yaratiladi) ----
language_enum = postgresql.ENUM("uz", "ru", "en", name="language_enum")
theme_enum = postgresql.ENUM("system", "light", "dark", name="theme_enum")
gender_enum = postgresql.ENUM("male", "female", "other", name="gender_enum")
goal_enum = postgresql.ENUM("lose_weight", "maintain", "gain_weight", "health", name="goal_enum")
risk_level_enum = postgresql.ENUM("safe", "moderate", "dangerous", name="risk_level_enum")
analysis_status_enum = postgresql.ENUM("pending", "success", "failed", name="analysis_status_enum")
ai_provider_enum = postgresql.ENUM("openai", "gemini", name="ai_provider_enum")


def _col_enum(enum: postgresql.ENUM) -> postgresql.ENUM:
    """Jadval ichida ishlatish uchun (turi allaqachon yaratilgan)."""
    return enum.copy().with_variant(enum, "postgresql")


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (
        language_enum,
        theme_enum,
        gender_enum,
        goal_enum,
        risk_level_enum,
        analysis_status_enum,
        ai_provider_enum,
    ):
        enum.create(bind, checkfirst=True)

    # ---------------- users ----------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(64)),
        sa.Column("first_name", sa.String(128)),
        sa.Column("last_name", sa.String(128)),
        sa.Column("photo_url", sa.String(512)),
        sa.Column("language_code", sa.String(8)),
        sa.Column("language", sa.Enum("uz", "ru", "en", name="language_enum", create_type=False), nullable=False, server_default="uz"),
        sa.Column("theme", sa.Enum("system", "light", "dark", name="theme_enum", create_type=False), nullable=False, server_default="system"),
        sa.Column("age", sa.Integer()),
        sa.Column("gender", sa.Enum("male", "female", "other", name="gender_enum", create_type=False)),
        sa.Column("height_cm", sa.Integer()),
        sa.Column("weight_kg", sa.Numeric(5, 2)),
        sa.Column("goal", sa.Enum("lose_weight", "maintain", "gain_weight", "health", name="goal_enum", create_type=False)),
        sa.Column("chronic_conditions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("allergies", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("daily_calorie_target", sa.Integer()),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    # ---------------- additives_catalog ----------------
    op.create_table(
        "additives_catalog",
        sa.Column("e_code", sa.String(16), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("category", sa.String(128)),
        sa.Column("risk_level", sa.Enum("safe", "moderate", "dangerous", name="risk_level_enum", create_type=False), nullable=False, server_default="safe"),
        sa.Column("description_uz", sa.Text()),
        sa.Column("description_ru", sa.Text()),
        sa.Column("description_en", sa.Text()),
    )

    # ---------------- analyses ----------------
    op.create_table(
        "analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.String(1024), nullable=False),
        sa.Column("image_hash", sa.String(64)),
        sa.Column("provider", sa.Enum("openai", "gemini", name="ai_provider_enum", create_type=False)),
        sa.Column("status", sa.Enum("pending", "success", "failed", name="analysis_status_enum", create_type=False), nullable=False, server_default="pending"),
        sa.Column("food_name", sa.String(256)),
        sa.Column("confidence", sa.Numeric(4, 3)),
        sa.Column("portion_estimate_g", sa.Numeric(7, 2)),
        sa.Column("calories", sa.Numeric(8, 2)),
        sa.Column("protein_g", sa.Numeric(7, 2)),
        sa.Column("carbs_g", sa.Numeric(7, 2)),
        sa.Column("fat_g", sa.Numeric(7, 2)),
        sa.Column("fiber_g", sa.Numeric(7, 2)),
        sa.Column("sugar_g", sa.Numeric(7, 2)),
        sa.Column("sodium_mg", sa.Numeric(8, 2)),
        sa.Column("ingredients", postgresql.JSONB()),
        sa.Column("additives", postgresql.JSONB()),
        sa.Column("allergen_matches", postgresql.JSONB()),
        sa.Column("risk_level", sa.Enum("safe", "moderate", "dangerous", name="risk_level_enum", create_type=False)),
        sa.Column("risk_score", sa.Integer()),
        sa.Column("risk_reasons", postgresql.JSONB()),
        sa.Column("personalized_warning", sa.Text()),
        sa.Column("raw_ai_response", postgresql.JSONB()),
        sa.Column("ai_latency_ms", sa.Integer()),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_analyses_user_id", "analyses", ["user_id"])
    op.create_index("ix_analyses_image_hash", "analyses", ["image_hash"])
    op.create_index("ix_analyses_user_created", "analyses", ["user_id", "created_at"])
    op.create_index("ix_analyses_risk", "analyses", ["user_id", "risk_level"])

    # ---------------- daily_summaries ----------------
    op.create_table(
        "daily_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("total_analyses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("safe_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("moderate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dangerous_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_calories", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "day", name="uq_daily_summaries_user_day"),
    )
    op.create_index("ix_daily_summaries_user_id", "daily_summaries", ["user_id"])


def downgrade() -> None:
    op.drop_table("daily_summaries")
    op.drop_table("analyses")
    op.drop_table("additives_catalog")
    op.drop_table("users")

    bind = op.get_bind()
    for enum in (
        ai_provider_enum,
        analysis_status_enum,
        risk_level_enum,
        goal_enum,
        gender_enum,
        theme_enum,
        language_enum,
    ):
        enum.drop(bind, checkfirst=True)
