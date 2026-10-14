"""AI promptlari va JSON sxemasi tavsifi.

Muhim tamoyil: AI FAQAT kuzatiladigan faktlarni (taom nomi, ozuqa qiymati,
tarkib, allergen bayroqlari, qo'shimchalar) qaytaradi. Shaxsiy xulosa
(risk) `risk_engine` da hisoblanadi.
"""

from __future__ import annotations

import json

from app.services.ai.base import ProfileContext

SYSTEM_PROMPT = """You are a food safety vision analyst for a health application.
You receive a photo of a meal, a food product package, or an ingredient list (label).

Return ONLY a single valid JSON object (no markdown, no commentary) with this exact schema:

{
  "food_name": string,
  "confidence": number,                 // 0..1, your certainty
  "portion_estimate_g": number,         // estimated portion weight in grams
  "nutrition": {
    "calories": number,                 // kcal for the estimated portion
    "protein_g": number,
    "carbs_g": number,
    "fat_g": number,
    "fiber_g": number,
    "sugar_g": number,
    "sodium_mg": number
  },
  "ingredients": [
    { "name": string, "category": string|null, "is_additive": boolean,
      "e_code": string|null, "risk": "safe"|"moderate"|"dangerous", "note": string|null }
  ],
  "additives": [
    { "e_code": string|null, "name": string, "risk": "safe"|"moderate"|"dangerous" }
  ],
  "allergen_flags": [ string ],          // e.g. ["gluten","lactose","nuts","peanut","egg","soy","fish","shellfish","sesame","honey"]
  "base_risk": "safe"|"moderate"|"dangerous",
  "barcode": { "value": string|null, "product_name": string|null }
}

Rules:
- If the image is not food or unreadable, set food_name to a short description, confidence <= 0.3, base_risk "moderate", empty arrays.
- Estimate nutrition per the visible portion; if the image is a label, use per-100g values but keep portion_estimate_g as 100.
- List known harmful/suspicious E-additives in "additives" with a risk rating.
- "allergen_flags" must use ONLY the vocabulary listed above (lowercase, English).
- Never invent exact nutrition data; give best-effort estimates.
- Output JSON only.
"""


def build_user_text(context: ProfileContext) -> str:
    """Foydalanuvchi kontekstini qisqa matn ko'rinishida promptga qo'shadi."""
    parts = [f"User language: {context.language}."]
    if context.allergies:
        parts.append(f"Known allergies: {', '.join(context.allergies)}.")
    if context.conditions:
        parts.append(f"Chronic conditions: {', '.join(context.conditions)}.")
    if context.goal:
        parts.append(f"Health goal: {context.goal}.")
    parts.append("Analyze the attached image and return the JSON object described in the system prompt.")
    return " ".join(parts)


def parse_json_response(text: str) -> dict:
    """AI matnidan JSON ajratib oladi (```json ... ``` bloklarini ham).

    Xato bo'lsa `ValueError` ko'taradi.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # ```json ... ``` yoki ``` ... ``` bloklarini olib tashlaymiz
        cleaned = cleaned[3:]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        if "```" in cleaned:
            cleaned = cleaned.split("```", 1)[0]
        cleaned = cleaned.strip()
    # Ba'zan matn ichida qo'shimcha bo'ladi — birinchi { dan oxirgi } gacha olamiz
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI JSON emas: {exc}") from exc


__all__ = ["SYSTEM_PROMPT", "build_user_text", "parse_json_response"]
