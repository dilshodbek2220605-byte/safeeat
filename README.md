# 🥗 SafeEat AI (TozaRasion)

Oziq-ovqat va suv xavfsizligini **AI orqali** tahlil qiluvchi ko'p tilli **Telegram Mini App**.

Foydalanuvchi taom yoki mahsulot tarkibi rasmini yuboradi — AI Vision tarkibni o'qib,
E-qo'shimchalarni aniqlaydi va **foydalanuvchi profiliga (allergiya, kasallik, maqsad) mos
ravishda** 🟢 Xavfsiz / 🟡 Me'yorda / 🔴 Taqiqlangan degan xulosa beradi.

---

## 🧱 Arxitektura

```
safeeat-ai/
├── apps/
│   ├── api/     FastAPI + SQLAlchemy 2.0 (async) + Alembic + aiogram
│   └── web/     Vite + React + TailwindCSS (Telegram Mini App)
├── packages/
│   └── shared-types/   AI JSON shartnomasi (TypeScript)
├── docker-compose.yml
└── .env.example
```

**Asosiy printsip:** AI faqat **faktlarni** ajratadi (taom, ozuqa qiymati, tarkib, E-qo'shimchalar,
allergen bayroqlari). **Shaxsiy xavf** esa `risk_engine`da **deterministik** qoidalar bilan
hisoblanadi — bu LLM "galyutsinatsiyasi"ni yo'q qiladi va natija izchil bo'ladi.

```
Rasm → image.py (resize/EXIF strip/hash) → storage.py (local|S3)
      → ai/factory.py (OpenAI → Gemini fallback) → AIResult (Pydantic strict)
      → risk_engine.py (profil bilan kesishadi) → analyses + daily_summaries
```

## Texnologiyalar

| Qatlam     | Stack |
|------------|-------|
| Frontend   | React 18 + Vite + TypeScript, TailwindCSS, `@twa-dev/sdk`, TanStack Query, Zustand, Framer Motion, i18next (uz/ru/en) |
| Backend    | FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, aiogram 3.x |
| Ma'lumotlar| PostgreSQL 16 (JSONB), Redis (rate-limit / replay) |
| AI         | OpenAI GPT-4o Vision (asosiy) → Gemini 1.5 Flash (fallback) |
| Auth       | Telegram `initData` HMAC-SHA256 → JWT (access + refresh) |
| Infra      | Docker Compose, Nginx, GitHub Actions |

---

## 🚀 Tez boshlash

### 1. Sozlamalar

```bash
cp .env.example .env
```

`.env` ichida majburiy: `BOT_TOKEN`, `JWT_SECRET` (`openssl rand -hex 32`), `OPENAI_API_KEY` yoki `GEMINI_API_KEY`.

### 2. Docker bilan (tavsiya)

```bash
docker compose up --build -d
make seed          # E-qo'shimchalar katalogini yuklash
```

- Backend (API docs): http://localhost:8000/docs
- Frontend (TMA): http://localhost:5173
- Telegram bot: long-polling (development)

### 3. Qo'lda (dev)

**Backend:**
```bash
cd apps/api
python -m venv .venv && .venv/Scripts/activate     # Windows
# source .venv/bin/activate                        # Linux/macOS
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

**Bot:**
```bash
cd apps/api
python -m app.bot.main
```

### 4. Bulutga joylash (production)

Render.com'ga (PostgreSQL + API + Mini App) bepul joylash bo'yicha to'liq
qo'llanma: **[`DEPLOY.md`](./DEPLOY.md)**. Konfiguratsiya: [`render.yaml`](./render.yaml).

---

## 🔌 API endpointlar (`/api/v1`)

| Method | Path | Tavsif |
|--------|------|--------|
| `POST` | `/auth/telegram` | `initData` tekshirish → JWT |
| `POST` | `/auth/refresh` | Refresh token → yangi access token |
| `GET`  | `/auth/me` | Joriy foydalanuvchi |
| `GET`  | `/users/me` | Profil |
| `PATCH`| `/users/me` | Profilni qismiy yangilash |
| `POST` | `/users/me/onboarding` | Onboarding yakunlash (kaloriya maqsadi hisoblanadi) |
| `POST` | `/analyses` | **Rasm → AI tahlil** (multipart `image`) |
| `GET`  | `/analyses` | Tarix (limit/offset, `risk`, `date_from/to`) |
| `GET`  | `/analyses/{id}` | Bitta natija |
| `DELETE`| `/analyses/{id}` | O'chirish |
| `GET`  | `/stats/summary` | Umumiy statistika |
| `GET`  | `/stats/calendar?year&month` | Oylik kalendar |
| `GET`  | `/catalog/additives` | E-qo'shimchalar katalogi |
| `GET`  | `/health` | Health check |

### Autentifikatsiya

1. Frontend `Telegram.WebApp.initData`'ni `POST /auth/telegram`ga yuboradi.
2. Backend HMAC-SHA256 bilan tekshiradi (`secret = HMAC("WebAppData", BOT_TOKEN)`) va `auth_date` yangiligini nazorat qiladi.
3. JWT access token qaytariladi (`Authorization: Bearer ...`).

---

## 🧠 AI JSON shartnomasi

AI faqat quyidagini qaytaradi (qat'iy Pydantic validatsiya):

```json
{
  "food_name": "Shokoladli tort",
  "confidence": 0.92,
  "portion_estimate_g": 150,
  "nutrition": { "calories": 450, "protein_g": 6, "carbs_g": 55, "fat_g": 22, "sugar_g": 40, "sodium_mg": 180 },
  "ingredients": [{ "name": "Wheat flour", "risk": "moderate" }],
  "additives": [{ "e_code": "E322", "name": "Lecithin", "risk": "safe" }],
  "allergen_flags": ["gluten", "nuts"],
  "base_risk": "moderate"
}
```

`risk_engine.py` esa profil bilan kesishib `risk_level`, `risk_score`, `risk_reasons` va
tarjima qilingan `personalized_warning`ni hisoblaydi.

---

## 🗄️ Ma'lumotlar modeli

- **users** — `telegram_id`, til/tema, yosh/jins/bo'y/vazn, maqsad, `chronic_conditions[]`, `allergies[]`, kaloriya maqsadi
- **analyses** — rasm URL/hash, AI natijasi (ozuqa + JSONB tarkib), `risk_level/score/reasons`, ogohlantirish
- **daily_summaries** — kalendar uchun kunlik jamlanma (yashil/sariq/qizil)
- **additives_catalog** — E-qo'shimchalar ma'lumotnomasi (seed)

Migratsiya: `alembic/versions/0001_initial.py`

---

## 🔐 Xavfsizlik

- `initData` HMAC tekshiruvi + `auth_date` yangiligi (replay himoyasi Redis'da)
- JWT (access 30 daq, refresh 30 kun)
- Rate limiting: `POST /analyses` — foydalanuvchi boshiga soatiga `RATE_LIMIT_ANALYSES_PER_HOUR`
- Rasm: MIME va hajm tekshiruvi, **EXIF (jumladan GPS) olib tashlanadi**, resize
- CORS faqat `CORS_ORIGINS`ga; loglarda maxfiy ma'lumot yo'q

---

## 🧪 Testlar

```bash
make test-api        # pytest (SQLite in-memory, AI mock)
make test-web        # vitest
make lint            # ruff + eslint
```

Backend testlari haqiqiy PostgreSQL talab qilmaydi (portativ turlar: `JSONType`/`GUID`).

---

## 🌍 Lokalizatsiya

- **Frontend:** `react-i18next` — `src/i18n/{uz,ru,en}.json`
- **Backend:** `services/localize.py` — ogohlantirishlar kod bo'yicha tayyor shablonlardan

---

## 📁 Muhim fayllar

| Fayl | Vazifasi |
|------|----------|
| `app/core/security.py` | initData HMAC + JWT |
| `app/services/analysis_service.py` | To'liq tahlil pipeline |
| `app/services/risk_engine.py` | Deterministik shaxsiy xavf |
| `app/services/ai/factory.py` | Provayder fallback orkestratori |
| `app/services/storage.py` | Local/S3 adapter |
| `web/src/lib/api.ts` | Token + refresh bilan API klient |
| `web/src/components/analyze/` | Kamera → tahlil → natija oqimi |
| `web/src/components/dashboard/HealthCalendar.tsx` | Salomatlik kalendari |

---

## 📈 Keyingi qadamlar (roadmap)

- Shtrix-kod (barcode) bazasidan mahsulot qidirish (Open Food Facts)
- Push-eslatmalar (aiogram orqali)
- Haftalik/oylik PDF hisobot
- AI xarajat monitoringi va kvotalar
- `packages/shared-types`dan kod generatsiyasi (OpenAPI)
