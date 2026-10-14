"""Deterministik xavf dvigateli.

AI faqat faktlarni beradi; shaxsiy xulosa shu yerda — foydalanuvchi profili
(allergiyalar, surunkali kasalliklar, maqsad) asosida qat'iy qoida bilan
hisoblanadi. Bu LLM'ning "galyutsinatsiya" xavfini yo'q qiladi.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.enums import Goal, Language, RiskLevel
from app.schemas.ai_result import AIResult
from app.services import localize

# ---- Chegaralar (me'yor ko'rsatkichlari) ----
SUGAR_HIGH_G = 15.0        # bir porsiyada yuqori shakar
SODIUM_HIGH_MG = 600.0     # yuqori natriy
CALORIES_HIGH = 500.0      # yuqori kaloriya
FAT_HIGH_G = 25.0          # yuqori yog'

# Scoring og'irliklari
W_ALLERGY = 100
W_BANNED_ADDITIVE = 80
W_HIGH_ADDITIVE = 25
W_SUGAR = 30
W_SODIUM = 25
W_CALORIES = 15
W_FAT = 15
W_BASE_DANGEROUS = 70
W_BASE_MODERATE = 25

# Kasallik → allergen/komponent xaritasi
_ALLERGEN_SYNONYMS = {
    "lactose": {"lactose", "milk", "dairy"},
    "nuts": {"nuts", "treenuts", "hazelnut", "almond", "walnut"},
    "peanut": {"peanut", "groundnut"},
    "gluten": {"gluten", "wheat", "barley", "rye"},
    "egg": {"egg", "eggs"},
    "soy": {"soy", "soya", "soybean"},
    "fish": {"fish"},
    "shellfish": {"shellfish", "shrimp", "crab"},
    "sesame": {"sesame"},
}


@dataclass
class RiskResult:
    risk_level: RiskLevel
    risk_score: int
    reasons: list[dict] = field(default_factory=list)
    personalized_warning: str | None = None


class RiskEngine:
    """Profilga moslashtirilgan xavf hisoblagichi."""

    def __init__(self, *, language: Language, allergies: list[str], conditions: list[str], goal: Goal | None = None):
        self.language = language
        self.allergies = {a.lower() for a in allergies}
        self.conditions = {c.lower() for c in conditions}
        self.goal = goal

    # --------------------------- public API --------------------------- #
    def evaluate(self, ai: AIResult) -> RiskResult:
        score = 0
        reasons: list[dict] = []

        # 1) Aniqlangan allergiyalar (eng jiddiy)
        matched_allergens = self._match_allergens(ai)
        for allergen in matched_allergens:
            score += W_ALLERGY
            reasons.append(
                self._reason(
                    "allergy_match",
                    RiskLevel.dangerous,
                    ref=localize.label(allergen, self.language),
                )
            )

        # 2) Surunkali kasalliklar
        score += self._evaluate_conditions(ai, reasons)

        # 3) Xavfli E-qo'shimchalar
        score += self._evaluate_additives(ai, reasons)

        # 4) Umumiy qoida: shakar / natriy / kaloriya / yog'
        score += self._evaluate_limits(ai, reasons)

        # 5) AI'ning umumiy bahosi
        if ai.base_risk == RiskLevel.dangerous:
            score += W_BASE_DANGEROUS
            reasons.append(self._reason("base_risk_dangerous", RiskLevel.dangerous))
        elif ai.base_risk == RiskLevel.moderate:
            score += W_BASE_MODERATE
            reasons.append(self._reason("base_risk_moderate", RiskLevel.moderate))

        score = min(score, 100)

        # Allergiya aniqlansa — har doim "dangerous"
        if matched_allergens:
            level = RiskLevel.dangerous
        elif score >= 65:
            level = RiskLevel.dangerous
        elif score >= 30:
            level = RiskLevel.moderate
        else:
            level = RiskLevel.safe

        warning = self._build_warning(level, reasons)
        return RiskResult(risk_level=level, risk_score=score, reasons=reasons, personalized_warning=warning)

    # --------------------------- internals --------------------------- #
    def _match_allergens(self, ai: AIResult) -> list[str]:
        detected = {flag.lower() for flag in ai.allergen_flags}
        ingredient_text = " ".join(
            f"{ing.name} {ing.note or ''}".lower() for ing in ai.ingredients
        )
        matched: list[str] = []
        for allergy in self.allergies:
            synonyms = _ALLERGEN_SYNONYMS.get(allergy, {allergy})
            if synonyms & detected or any(word in ingredient_text for word in synonyms):
                matched.append(allergy)
        return sorted(set(matched))

    def _evaluate_conditions(self, ai: AIResult, reasons: list[dict]) -> int:
        score = 0
        n = ai.nutrition

        if "diabetes" in self.conditions and n.sugar_g >= SUGAR_HIGH_G:
            score += W_SUGAR
            reasons.append(
                self._reason("condition_sugar", RiskLevel.moderate, ref=f"{n.sugar_g:.1f}")
            )

        if "hypertension" in self.conditions and n.sodium_mg >= SODIUM_HIGH_MG:
            score += W_SODIUM
            reasons.append(
                self._reason("condition_sodium", RiskLevel.moderate, ref=f"{n.sodium_mg:.0f}")
            )

        if "celiac" in self.conditions and ("gluten" in {f.lower() for f in ai.allergen_flags} or self._contains_gluten(ai)):
            score += W_ALLERGY
            reasons.append(self._reason("condition_gluten", RiskLevel.dangerous))

        if "high_cholesterol" in self.conditions and n.fat_g >= FAT_HIGH_G:
            score += W_FAT
            reasons.append(self._reason("condition_fat", RiskLevel.moderate))

        return score

    def _contains_gluten(self, ai: AIResult) -> bool:
        text = " ".join(f"{i.name} {i.note or ''}".lower() for i in ai.ingredients)
        return any(word in text for word in ("wheat", "gluten", "barley", "rye"))

    def _evaluate_additives(self, ai: AIResult, reasons: list[dict]) -> int:
        score = 0
        for additive in ai.additives:
            ref = additive.e_code or additive.name
            if additive.risk == RiskLevel.dangerous:
                score += W_BANNED_ADDITIVE
                reasons.append(self._reason("banned_additive", RiskLevel.dangerous, ref=ref))
            elif additive.risk == RiskLevel.moderate:
                score += W_HIGH_ADDITIVE
                reasons.append(self._reason("high_risk_additive", RiskLevel.moderate, ref=ref))
        return score

    def _evaluate_limits(self, ai: AIResult, reasons: list[dict]) -> int:
        score = 0
        n = ai.nutrition

        # Yuqori kaloriya — ayniqsa "lose_weight" maqsadida
        if n.calories >= CALORIES_HIGH:
            weight = W_CALORIES * (2 if self.goal == Goal.lose_weight else 1)
            score += weight
            reasons.append(self._reason("high_calories", RiskLevel.moderate, ref=f"{n.calories:.0f}"))

        return score

    def _reason(self, code: str, severity: RiskLevel, ref: str | None = None) -> dict:
        return {
            "code": code,
            "severity": severity,
            "message": localize.t(code, self.language, ref=ref or ""),
            "ref": ref,
        }

    def _build_warning(self, level: RiskLevel, reasons: list[dict]) -> str:
        if not reasons:
            return localize.t("all_clear", self.language)
        # Eng jiddiy sababni birinchi qilib, matnlarini birlashtiramiz
        severity_rank = {RiskLevel.dangerous: 0, RiskLevel.moderate: 1, RiskLevel.safe: 2}
        ordered = sorted(reasons, key=lambda r: severity_rank[r["severity"]])
        messages = [r["message"] for r in ordered[:3]]
        return " ".join(messages)
