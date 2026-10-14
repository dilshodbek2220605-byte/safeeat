# 🚀 SafeEat AI — Render.com'ga joylash (deploy)

Bu qo'llanma loyihani **bepul** tarifda Render.com'ga joylashni bosqichma-bosqich
tushuntiradi: PostgreSQL + FastAPI backend + React Mini App.

Blueprint fayli: [`render.yaml`](./render.yaml)

---

## Tartib (umumiy ko'rinish)

1. GitHub'ga kodni yuklash
2. Render'da Blueprint bilan uchta resursni yaratish
3. Sirlarni (BOT_TOKEN, AI kalitlar) kiritish
4. Deploy natijasini tekshirish
5. BotFather'da Mini App'ni ro'yxatdan o'tkazish
6. Botni ishga tushirish (3 variant)
7. Muhim cheklovlar va ularni yechish

---

## 1. Kodni GitHub'ga yuklash

Render GitHub'dagi repo'dan o'qiydi. Bu papka hozircha git repo emas:

```bash
cd C:\Users\user\Desktop\loyiha
git init
git add .
git commit -m "SafeEat AI (TozaRasion)"
git branch -M main
```

Keyin GitHub'da **bo'sh** repo yarating (masalan `safeeat-ai`) va ulang:

```bash
git remote add origin https://github.com/<USERNAME>/safeeat-ai.git
git push -u origin main
```

> **Xavfsizlik:** `.gitignore` `.env`, `.venv/`, `node_modules/`, `*.db` ni
> chiqarib tashlaydi — token va parollar GitHub'ga tushmaydi. Buni `git status`
> bilan tekshirib oling: ro'yxatda `.env` **bo'lmasligi** kerak.

---

## 2. Render'da Blueprint bilan joylash

1. [dashboard.render.com/register](https://dashboard.render.com/register) —
   **GitHub** bilan ro'yxatdan o'ting.
2. **New +** → **Blueprint**.
3. Repo'ni tanlang (`safeeat-ai`) → **Connect**.
4. Render `render.yaml` ni o'qib, quyidagilarni ko'rsatadi:
   - `safeeat-db` — PostgreSQL (free)
   - `safeeat-api` — backend (Docker, free)
   - `safeeat-web` — frontend (static, free)
5. Sirlar so'raladi (`sync: false`):
   | Kalit | Nima yoziladi |
   |---|---|
   | `BOT_TOKEN` | @BotFather bergan token |
   | `OPENAI_API_KEY` | OpenAI kaliti (bo'sh qoldirsangiz ham bo'ladi) |
   | `GEMINI_API_KEY` | Gemini kaliti (ixtiyoriy, fallback) |
6. **Apply** / **Create Resources** → deploy boshlanadi (birinchi marta ~5-10 daqiqa).

Deploy paytida avtomatik bajariladi:
- `alembic upgrade head` — jadvallar yaratiladi (`preDeployCommand`)
- `python -m app.db.seed` — 25 ta E-qo'shimcha yuklanadi (`initialDeployHook`)

> ⚠️ Bepul web service'da **Shell yo'q**, shuning uchun seed aynan shu hook orqali
> bajariladi. Agar jadval/katalog bo'sh qolsa, `render.yaml` dan `initialDeployHook`
> ni o'chirib-bir yoqib qayta deploy qiling.

---

## 3. Natijani tekshirish

| Tekshiruv | Kutilgan natija |
|---|---|
| `https://safeeat-api.onrender.com/api/v1/health` | `{"status":"ok","database":true}` |
| `https://safeeat-api.onrender.com/api/v1/catalog/additives?limit=1` | Bo'sh bo'lmagan JSON massiv |
| `https://safeeat-web.onrender.com` | Sahifa ochiladi (login xatosi — **normal**, chunki brauzerda Telegram `initData` yo'q) |

> ❗ **Agar manzillar boshqacha bo'lsa** (Render xizmat nomini band deb boshqa
> subdomain berganda), `render.yaml` dagi **uch joyni** yangilang va qayta deploy qiling:
> `WEBAPP_URL`, `CORS_ORIGINS`, `VITE_API_BASE_URL`.
> `API_PUBLIC_URL` esa avtomatik to'g'ri oladi (`fromService`).

---

## 4. BotFather'da Mini App'ni ro'yxatdan o'tkazish

Bu qadam mini-ilovani Telegram ichida ochish uchun kerak.

1. **@BotFather** → `/newapp` → botni tanlang
2. **Title**: `SafeEat AI`
3. **Description**: qisqa tavsif
4. **Photo**: 512×512 rasm (yoki `/empty`)
5. **Web App URL**: `https://safeeat-web.onrender.com`  ← **Render manzili, localhost emas!**
6. **Short name**: masalan `safeeat`
7. Natija: `t.me/<bot_username>/safeeat`

Qo'shimcha (tavsiya):

- `/setmenubutton` → bot tanlang → URL: `https://safeeat-web.onrender.com`
- `/setcommands`:
  ```
  start - Botni ishga tushirish
  help - Yordam
  ```

Endi Mini App'ni **bot jarayoni ishlamasa ham** shu havola orqali ochish mumkin.

---

## 5. Botni ishga tushirish — 3 variant

### A) Bepul: o'z kompyuteringizda (long-polling) ✅ tavsiya etiladi

```bash
cd C:\Users\user\Desktop\loyiha
# .env ichida:
#   BOT_TOKEN=<haqiqiy token>
#   WEBAPP_URL=https://safeeat-web.onrender.com
cd apps/api
.venv\Scripts\python.exe -m app.bot.main
```

Kompyuter yoqilgan va internet bor ekan, bot `/start` ga javob beradi.
Backend endi Render'da bo'lgani uchun kompyuterda PostgreSQL/Vite kerak emas.

### B) Pulli: Render background worker (~$7/oy, 24/7)

`render.yaml` oxiridagi `safeeat-bot` blokini izohdan chiqaring va deploy qiling.
U `ENV=development` bilan long-polling'da ishlaydi (port/webhook kerak emas).

### C) Botsiz

Botga umuman ehtiyoj yo'q — mini-ilova `t.me/<bot>/<shortname>` havolasi orqali
ochiladi (4-qadam). Bu holda `/start` javob bermaydi.

---

## 6. Bepul tarifning muhim cheklovlari

| Cheklov | Ta'siri | Yechim |
|---|---|---|
| **15 daq. harakatsizlikdan keyin uxlaydi** | Keyingi so'rov ~1 daqiqa kutadi (Mini App "osilib" qoladi) | [cron-job.org](https://cron-job.org) bilan har 5-10 daqiqada `https://safeeat-api.onrender.com/api/v1/health` ni urib turing |
| **Fayl tizimi vaqtinchalik** | Yuklangan rasmlar spin-down/redeploy'da **o'chib ketadi** | `STORAGE_BACKEND=s3` qiling (Cloudflare R2 — 10 GB bepul). `.env`/Render env: `S3_*` qiymatlari |
| **Bepul PostgreSQL 30 kundan keyin muddati tugaydi** | Baza o'chadi (14 kunlik "grace" bor) | Vaqtida pulli planga o'tkazing **yoki** tashqi bepul Postgres (Neon/Supabase) ishlatib `DATABASE_URL` ni qo'lda bering |
| **Bitta bepul PostgreSQL** | Ikkinchisini yaratib bo'lmaydi | Mavjudini ishlating |
| **750 instance-soat/oy** | 24/7 ishlaganda ~720 soat ketadi | Uxlab turishi soatni tejaydi — keep-alive'ni faqat kerak bo'lganda yoqing |
| **Build pipeline daqiqalari** | Ko'p deploy = limit tugashi | Kamdan-kam push qiling |

> Batafsil: <https://render.com/docs/free>

---

## 7. Muhit o'zgaruvchilari (Render → safeeat-api → Environment)

| Kalit | Qiymat | Izoh |
|---|---|---|
| `ENV` | `production` | `/docs` o'chadi, bot webhook rejimida |
| `DATABASE_URL` | (avtomatik) | Blueprint'dan |
| `API_PUBLIC_URL` | (avtomatik) | `RENDER_EXTERNAL_URL` |
| `WEBAPP_URL` | `https://safeeat-web.onrender.com` | Mini App manzili |
| `CORS_ORIGINS` | `https://safeeat-web.onrender.com` | Frontend origin |
| `JWT_SECRET` | (avtomatik generatsiya) | O'zgartirmang — tokenlar bekor bo'ladi |
| `BOT_TOKEN` | sizning token | `/start` + `initData` HMAC uchun |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | kalitlar | Bo'lmasa rasm tahlili ishlamaydi |
| `REDIS_URL` | (berilmagan) | Yo'q — rate-limit "fail-open" ishlaydi |

---

## 8. Yangilash (keyingi deploylar)

```bash
git add .
git commit -m "o'zgarish izohi"
git push
```

Render `autoDeployTrigger: commit` bo'yicha avtomatik qayta deploy qiladi
(har safar `alembic upgrade head` ham ishlaydi).

---

## 9. Muammolarni bartaraf etish

| Alomat | Sabab / yechim |
|---|---|
| Build'da `tsc` xatosi | Lokal `npm run build` bilan tekshiring (o'tgan bo'lishi kerak) |
| `connect() failed` / DB xatosi | API va DB **bir xil region**da bo'lishi shart |
| `{"status":"ok","database":false}` | `DATABASE_URL` noto'g'ri yoki baza uxlagan |
| Mini App'da "Failed to fetch" / CORS | `CORS_ORIGINS` da web manzili yo'q |
| Rasmlar ko'rinmaydi, tahlil ishlaydi | `API_PUBLIC_URL` noto'g'ri (rasm URL'i shundan yasaladi) |
| Katalog bo'sh | `initialDeployHook` ishlamagan — qayta deploy qiling |
| Deploy `region` xatosi bilan yiqildi | `render.yaml` da `region` ni `oregon` ga o'zgartiring (DB va API bir xil) |
| Birinchi ochilishda 1 daqiqa kutish | Free tarif uyqudan uyg'onishi — bu normal |

---

## 10. VPS'ga o'tish (kelajakda arzon va cheklovsiz)

Loyihada `docker-compose.yml` bor — VPS'da deyarli bir xil ishlaydi:

```bash
git clone <repo> && cd safeeat-ai
cp .env.example .env   # BOT_TOKEN, JWT_SECRET, AI kalitlarni to'ldiring
docker compose up --build -d
make seed
```

Faqat HTTPS uchun oldiga Caddy/nginx + domen qo'yish kerak (Telegram WebApp https talab qiladi).
