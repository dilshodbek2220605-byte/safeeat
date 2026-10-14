"""Auth endpointlari: Telegram initData validatsiyasi va JWT berish."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.deps import CurrentUser, SessionDep
from app.core.rate_limit import mark_once
from app.core.security import (
    InitDataError,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_init_data,
)
from app.models.user import User
from app.schemas.auth import AuthResponse, RefreshRequest, TelegramAuthRequest, TokenPair
from app.schemas.user import UserRead
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(user_id) -> TokenPair:
    settings = get_settings()
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(payload: TelegramAuthRequest, session: SessionDep) -> AuthResponse:
    """`initData`ni tekshiradi, foydalanuvchini upsert qiladi va tokenlar qaytaradi."""
    data = verify_init_data(payload.init_data)

    tg_user = data.get("user")
    if not isinstance(tg_user, dict) or "id" not in tg_user:
        raise InitDataError("initData ichida foydalanuvchi ma'lumoti yo'q")

    # Replay protection: bir xil initData hash'i Redis'da kuzatiladi.
    # TMA qayta ochilganda bir xil initData kelishi mumkin, shuning uchun biz
    # qattiq blok qilmaymiz — lekin kuzatuv uchun belgilab qo'yamiz.
    init_hash = data.get("hash") or ""
    if init_hash:
        await mark_once(str(init_hash), ttl=get_settings().init_data_max_age_seconds)

    user, is_new = await user_service.upsert_from_telegram(session, tg_user)
    tokens = _issue_tokens(user.id)
    return AuthResponse(tokens=tokens, user=UserRead.model_validate(user), is_new_user=is_new)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, session: SessionDep) -> TokenPair:
    """Refresh token orqali yangi access token oladi."""
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token turi noto'g'ri")

    try:
        user_id = uuid.UUID(data["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token ichidagi sub yaroqsiz") from exc

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Foydalanuvchi topilmadi")

    return _issue_tokens(user.id)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    """Joriy foydalanuvchi (token tekshiruvi uchun qulay)."""
    return UserRead.model_validate(user)
