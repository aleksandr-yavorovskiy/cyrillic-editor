.PHONY: build build-dev up up-dev lint lint-backend lint-frontend format test-backend deploy

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
	.venv/bin/ruff check backend/.

lint-frontend:
	cd frontend && npm run lint

format:
	cd frontend && npm run format

test-backend:
	.venv/bin/python backend/manage.py test

deploy: build up
