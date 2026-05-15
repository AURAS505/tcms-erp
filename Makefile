.PHONY: help build up down logs backend-shell frontend-shell test-backend test-frontend lint-backend lint-frontend

help:
	@echo "TCMS ERP development commands"
	@echo "  make build           Build Docker images"
	@echo "  make up              Start local services"
	@echo "  make down            Stop local services"
	@echo "  make logs            Tail service logs"
	@echo "  make backend-shell   Open a backend shell"
	@echo "  make frontend-shell  Open a frontend shell"
	@echo "  make test-backend    Run backend tests"
	@echo "  make test-frontend   Run frontend tests"

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

logs:
	docker compose logs -f

backend-shell:
	docker compose run --rm backend sh

frontend-shell:
	docker compose run --rm frontend sh

test-backend:
	docker compose run --rm backend pytest

test-frontend:
	docker compose run --rm frontend npm test

lint-backend:
	docker compose run --rm backend ruff check .

lint-frontend:
	docker compose run --rm frontend npm run lint
