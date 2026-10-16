FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Tizim kutubxonalari (Pillow uchun minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Avval faqat bog'liqliklarni o'rnatamiz (docker layer cache uchun)
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e ".[dev]"

# Ilova kodi
COPY . .

EXPOSE 8000

# Port `$PORT` orqali ham berilishi mumkin (Render va shunga o'xshash platformalar)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS "http://localhost:${PORT:-8000}/api/v1/health" || exit 1

CMD ["/bin/sh", "./start.sh"]
