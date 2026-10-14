# SafeEat AI — qulay buyruqlar (make <target>)
# Windows'da: `make` o'rniga buyruqni to'g'ridan-to'g'ri yozing yoki Git Bash ishlatilgan.

.PHONY: help up down logs api-shell migrate revision seed test-api test-web lint fmt

help:
	@echo "up            - docker compose bilan hammasini ko'tarish"
	@echo "down          - to'xtatish"
	@echo "logs          - loglarni kuzatish"
	@echo "migrate       - alembic upgrade head"
	@echo "revision m=.. - yangi migratsiya (m=\\\"...\\\")"
	@echo "seed          - E-qo'shimchalar katalogini yuklash"
	@echo "test-api      - pytest"
	@echo "test-web      - vitest"
	@echo "lint          - ruff + eslint"
	@echo "fmt           - ruff format + prettier"

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

api-shell:
	docker compose exec api sh

migrate:
	cd apps/api && alembic upgrade head

revision:
	cd apps/api && alembic revision --autogenerate -m "$(m)"

seed:
	cd apps/api && python -m app.db.seed

test-api:
	cd apps/api && pytest -q

test-web:
	cd apps/web && npm run test

lint:
	cd apps/api && ruff check .
	cd apps/web && npm run lint

fmt:
	cd apps/api && ruff format .
	cd apps/web && npm run format
