#!/bin/sh
set -e

echo "=== Starting SafeEat API ==="
echo "PORT=${PORT:-8000}"
echo "ENV=${ENV:-development}"

echo "=== Running migrations ==="
alembic upgrade head
echo "=== Migrations done ==="

echo "=== Running seed ==="
python -m app.db.seed
echo "=== Seed done ==="

echo "=== Starting uvicorn ==="
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
