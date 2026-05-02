.PHONY: build build-dev up up-dev deps deps-backend deps-frontend lint lint-backend lint-frontend format test-backend deploy

build:
	docker compose build

build-dev:
	docker compose -f docker-compose.dev.yml build

up:
	docker compose up

up-dev:
	docker compose -f docker-compose.dev.yml up

lint: lint-backend lint-frontend

lint-backend:
	ruff check backend/.

lint-frontend:
	cd frontend && npm run lint

deps: deps-backend deps-frontend

deps-backend:
	pip install -r backend/requirements.txt

deps-frontend:
	cd frontend && npm ci

format:
	cd frontend && npm run format

test-backend:
	cd backend && python -m pytest api/tests/ -v

deploy: build up
