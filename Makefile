.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: setup
setup: ## Initial project setup
	@echo "Setting up the project..."
	cp .env.example .env
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "✅ Environment files created. Please update them with your settings."

.PHONY: build
build: ## Build all Docker images
	docker-compose build

.PHONY: up
up: ## Start all services
	docker-compose up

.PHONY: up-d
up-d: ## Start all services in detached mode
	docker-compose up -d

.PHONY: down
down: ## Stop all services
	docker-compose down

.PHONY: restart
restart: down up ## Restart all services

.PHONY: logs
logs: ## View logs from all services
	docker-compose logs -f

.PHONY: logs-backend
logs-backend: ## View backend logs
	docker-compose logs -f backend

.PHONY: logs-frontend
logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

.PHONY: logs-db
logs-db: ## View database logs
	docker-compose logs -f mongodb

.PHONY: shell-backend
shell-backend: ## Open shell in backend container
	docker-compose exec backend bash

.PHONY: shell-frontend
shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend sh

.PHONY: shell-db
shell-db: ## Open MongoDB shell
	docker-compose exec mongodb mongosh

.PHONY: test
test: test-backend test-frontend ## Run all tests

.PHONY: test-backend
test-backend: ## Run backend tests
	docker-compose exec backend pytest

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	docker-compose exec frontend npm test

.PHONY: lint
lint: lint-backend lint-frontend ## Run linters for all code

.PHONY: lint-backend
lint-backend: ## Run backend linters
	docker-compose exec backend black .
	docker-compose exec backend flake8
	docker-compose exec backend isort .
	docker-compose exec backend mypy .

.PHONY: lint-frontend
lint-frontend: ## Run frontend linters
	docker-compose exec frontend npm run lint
	docker-compose exec frontend npm run type-check

.PHONY: format
format: format-backend format-frontend ## Format all code

.PHONY: format-backend
format-backend: ## Format backend code
	docker-compose exec backend black .
	docker-compose exec backend isort .

.PHONY: format-frontend
format-frontend: ## Format frontend code
	docker-compose exec frontend npx prettier --write .

.PHONY: clean
clean: ## Clean up generated files and containers
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

.PHONY: db-seed
db-seed: ## Seed database with sample data
	docker-compose exec backend python scripts/seed_db.py

.PHONY: db-backup
db-backup: ## Backup database
	docker-compose exec mongodb mongodump --out /backup/$(shell date +%Y%m%d_%H%M%S)

.PHONY: db-restore
db-restore: ## Restore database from latest backup
	docker-compose exec mongodb mongorestore /backup/$(shell ls -t backup/ | head -1)

.PHONY: update-deps
update-deps: ## Update all dependencies
	cd backend && pip-compile requirements.in
	cd frontend && npm update

.PHONY: check-security
check-security: ## Check for security vulnerabilities
	docker-compose exec backend pip-audit -r requirements.txt || echo "Backend security scan completed"
	docker-compose exec frontend npm audit || echo "Frontend security scan completed"