"""Foydalanuvchi profili endpointlari."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.schemas.user import OnboardingRequest, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_profile(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.patch("/me", response_model=UserRead)
async def update_profile(payload: UserUpdate, user: CurrentUser, session: SessionDep) -> UserRead:
    """Profilni qismiy yangilash."""
    data = payload.model_dump(exclude_unset=True)

    # Allergiya/kasalliklarni normallashtirish (kichik harf, takrorlarni olib tashlash)
    if "allergies" in data and data["allergies"] is not None:
        data["allergies"] = sorted({a.strip().lower() for a in data["allergies"] if a.strip()})
    if "chronic_conditions" in data and data["chronic_conditions"] is not None:
        data["chronic_conditions"] = sorted({c.strip().lower() for c in data["chronic_conditions"] if c.strip()})

    for field, value in data.items():
        setattr(user, field, value)

    await session.flush()
    await session.refresh(user)
    return UserRead.model_validate(user)


@router.post("/me/onboarding", response_model=UserRead)
async def complete_onboarding(payload: OnboardingRequest, user: CurrentUser, session: SessionDep) -> UserRead:
    """Onboarding yakunida to'liq profilni saqlaydi."""
    data = payload.model_dump()
    data["allergies"] = sorted({a.strip().lower() for a in data.get("allergies", []) if a.strip()})
    data["chronic_conditions"] = sorted({c.strip().lower() for c in data.get("chronic_conditions", []) if c.strip()})

    for field, value in data.items():
        setattr(user, field, value)

    user.onboarding_completed = True

    # Kaloriya maqsadini avtomatik hisoblash (agar berilmagan bo'lsa)
    if not user.daily_calorie_target:
        user.daily_calorie_target = _estimate_calorie_target(user)

    await session.flush()
    await session.refresh(user)
    return UserRead.model_validate(user)


def _estimate_calorie_target(user) -> int:
    """Mifflin-St Jeor formulasi asosida taxminiy kunlik kaloriya maqsadi."""
    from app.models.enums import Gender, Goal

    weight = float(user.weight_kg or 70)
    height = float(user.height_cm or 170)
    age = float(user.age or 30)
    # Bazal metabolizm (BMR)
    if user.gender == Gender.female:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    tdee = bmr * 1.4  # engil faollik
    if user.goal == Goal.lose_weight:
        tdee -= 400
    elif user.goal == Goal.gain_weight:
        tdee += 300
    return max(1200, int(round(tdee)))
