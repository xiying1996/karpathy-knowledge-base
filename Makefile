.PHONY: dev build up down test lint clean

dev:
	docker compose up --build

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

test:
	cd backend && python -m pytest

test-backend:
	cd backend && python -m pytest -v

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/app/__pycache
	rm -rf frontend/node_modules

install-backend-deps:
	cd backend && pip install -e ".[dev]"

install-frontend-deps:
	cd frontend && npm install

ruff-check:
	cd backend && ruff check .

ruff-fix:
	cd backend && ruff check --fix .

backend-shell:
	docker compose exec backend bash

frontend-shell:
	docker compose exec frontend sh

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend
