"""E-qo'shimchalar katalogini yuklash (seed).

Ishga tushirish:  python -m app.db.seed
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db.session import SessionLocal, engine
from app.models.additive import Additive
from app.models.enums import RiskLevel

# (e_code, name, category, risk, uz, ru, en)
ADDITIVES: list[tuple[str, str, str, RiskLevel, str, str, str]] = [
    ("E100", "Kurkumin", "Rang", RiskLevel.safe, "Tabiiy ziravor rangi", "Натуральный краситель", "Natural yellow color"),
    ("E102", "Tartrazin", "Rang", RiskLevel.moderate, "Sintetik sariq bo'yoq, allergik reaksiya mumkin", "Синтетический жёлтый краситель", "Synthetic yellow dye, may cause allergy"),
    ("E110", "Sunset Yellow", "Rang", RiskLevel.moderate, "Sintetik bo'yoq, bolalarda diqqatni pasaytiradi", "Синтетический краситель", "Synthetic dye, may affect children"),
    ("E120", "Karmin", "Rang", RiskLevel.safe, "Hasharotdan olinadigan qizil rang", "Красный краситель из насекомых", "Red color from insects"),
    ("E150d", "Karamel IV", "Rang", RiskLevel.moderate, "Sulfitli karamel rangi", "Сульфитный карамельный краситель", "Sulphite caramel color"),
    ("E171", "Titan dioksidi", "Rang", RiskLevel.dangerous, "Ba'zi davlatlarda taqiqlangan", "Запрещён в ряде стран", "Banned in several countries"),
    ("E200", "Sorbin kislotasi", "Konservant", RiskLevel.safe, "Xavfsiz konservant", "Безопасный консервант", "Safe preservative"),
    ("E202", "Kaliy sorbat", "Konservant", RiskLevel.safe, "Keng qo'llaniladigan konservant", "Распространённый консервант", "Common preservative"),
    ("E210", "Benzoy kislotasi", "Konservant", RiskLevel.moderate, "Astma uchun xavfli bo'lishi mumkin", "Может вредить при астме", "May harm asthmatics"),
    ("E211", "Natriy benzoat", "Konservant", RiskLevel.moderate, "Vitamin C bilan kanserogen hosil qilishi mumkin", "С витамином C может образовывать канцероген", "With vitamin C may form carcinogen"),
    ("E220", "Sulfit", "Konservant", RiskLevel.moderate, "Astma va sulfit allergiyasi", "Астма и аллергия на сульфиты", "Asthma and sulphite allergy"),
    ("E250", "Natriy nitrit", "Konservant", RiskLevel.dangerous, "Kolbasa mahsulotlari, yuqori dozada kanserogen", "Нитрит натрия, канцероген в высоких дозах", "Sodium nitrite, carcinogenic in high doses"),
    ("E251", "Natriy nitrat", "Konservant", RiskLevel.moderate, "Nitrat, ehtiyotkorlik bilan", "Нитрат, с осторожностью", "Nitrate, use with caution"),
    ("E260", "Sirka kislotasi", "Konservant", RiskLevel.safe, "Xavfsiz", "Безопасно", "Safe"),
    ("E300", "Askorbin kislotasi", "Antioksidant", RiskLevel.safe, "C vitamini", "Витамин C", "Vitamin C"),
    ("E320", "BHA", "Antioksidant", RiskLevel.dangerous, "Potensial kanserogen", "Потенциальный канцероген", "Potential carcinogen"),
    ("E321", "BHT", "Antioksidant", RiskLevel.moderate, "Shubhali antioksidant", "Спорный антиоксидант", "Controversial antioxidant"),
    ("E330", "Limon kislotasi", "Antioksidant", RiskLevel.safe, "Xavfsiz", "Безопасно", "Safe"),
    ("E407", "Karrageenan", "Quyultiruvchi", RiskLevel.moderate, "Hazm tizimiga ta'sir qilishi mumkin", "Может влиять на пищеварение", "May affect digestion"),
    ("E415", "Ksantan saqichi", "Quyultiruvchi", RiskLevel.safe, "Xavfsiz", "Безопасно", "Safe"),
    ("E420", "Sorbitol", "Shirinlashtiruvchi", RiskLevel.moderate, "Ko'p iste'molda ich ketishi", "Слабительное при избытке", "Laxative in excess"),
    ("E621", "Natriy glutamat", "Ta'm kuchaytiruvchi", RiskLevel.moderate, "Ba'zilarda bosh og'rig'i, sezgirlik", "У некоторых головная боль", "Headache in sensitive people"),
    ("E627", "Natriy guanilat", "Ta'm kuchaytiruvchi", RiskLevel.moderate, "Purini bor, podagra uchun ehtiyot", "Пурины, осторожно при подагре", "Purines, cautious with gout"),
    ("E951", "Aspartam", "Shirinlashtiruvchi", RiskLevel.dangerous, "Fenilketonuriya uchun taqiqlangan", "Запрещён при фенилкетонурии", "Forbidden in phenylketonuria"),
    ("E952", "Siklamat", "Shirinlashtiruvchi", RiskLevel.dangerous, "Ba'zi davlatlarda taqiqlangan", "Запрещён в ряде стран", "Banned in some countries"),
]


async def seed() -> None:
    async with SessionLocal() as session:
        for e_code, name, category, risk, uz, ru, en in ADDITIVES:
            existing = await session.scalar(select(Additive).where(Additive.e_code == e_code))
            if existing is None:
                session.add(
                    Additive(
                        e_code=e_code,
                        name=name,
                        category=category,
                        risk_level=risk,
                        description_uz=uz,
                        description_ru=ru,
                        description_en=en,
                    )
                )
            else:
                existing.name = name
                existing.category = category
                existing.risk_level = risk
                existing.description_uz = uz
                existing.description_ru = ru
                existing.description_en = en
        await session.commit()
    print(f"✅ {len(ADDITIVES)} ta E-qo'shimcha katalogga yuklandi")


async def _main() -> None:
    from app.core.logging import ensure_utf8_console

    ensure_utf8_console()
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
