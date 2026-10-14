"""Auth sxemalari."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class TelegramAuthRequest(BaseModel):
    """Frontend `Telegram.WebApp.initData` satrini yuboradi."""

    init_data: str = Field(min_length=10, alias="initData")

    model_config = {"populate_by_name": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 — OAuth2 standart qiymati
    expires_in: int  # access token umri (soniya)


class AuthResponse(BaseModel):
    tokens: TokenPair
    user: UserRead
    is_new_user: bool
