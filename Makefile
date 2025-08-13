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
test-backend: ## Run backend tests with coverage
	docker-compose exec backend pytest --cov=src --cov-report=term-missing --cov-fail-under=80

.PHONY: test-frontend
test-frontend: ## Run frontend tests (when implemented)
	docker-compose exec frontend npm test

.PHONY: lint
lint: lint-backend lint-frontend ## Run linters for all code

.PHONY: lint-backend
lint-backend: ## Run backend linters and fix issues
	docker-compose exec backend black .
	docker-compose exec backend isort .
	docker-compose exec backend flake8 .
	docker-compose exec backend mypy .

.PHONY: lint-frontend
lint-frontend: ## Run frontend linters
	docker-compose exec frontend npm run lint --fix || true
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

.PHONY: dev-backend
dev-backend: ## Run backend in development mode (local)
	cd backend && source venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: dev-frontend
dev-frontend: ## Run frontend in development mode (local)
	cd frontend && npm run dev

.PHONY: build-frontend
build-frontend: ## Build frontend for production
	cd frontend && npm run build

.PHONY: install-backend
install-backend: ## Install backend dependencies (local)
	cd backend && pip install -r requirements.txt

.PHONY: install-frontend
install-frontend: ## Install frontend dependencies (local)
	cd frontend && npm install

.PHONY: install
install: install-backend install-frontend ## Install all dependencies (local)

.PHONY: api-docs
api-docs: ## Open API documentation in browser
	@echo "Opening API documentation at http://localhost:8000/docs"
	@command -v open >/dev/null 2>&1 && open http://localhost:8000/docs || echo "Visit http://localhost:8000/docs in your browser"

.PHONY: status
status: ## Check status of all services
	docker-compose ps

.PHONY: logs-all
logs-all: ## View logs from all services in real-time
	docker-compose logs -f --tail=50

.PHONY: health
health: ## Check health of all services
	@echo "Checking backend health..."
	@curl -s http://localhost:8000/health || echo "❌ Backend not responding"
	@echo "Checking frontend..."
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend is running" || echo "❌ Frontend not responding"
	@echo "Checking MongoDB..."
	@docker-compose exec mongodb mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1 && echo "✅ MongoDB is running" || echo "❌ MongoDB not responding"

.PHONY: quick-start
quick-start: ## Quick start for development (Docker)
	@echo "🚀 Starting Clinic Appointment System..."
	@echo "📦 Building containers..."
	docker-compose up --build -d
	@echo "⏳ Waiting for services to start..."
	sleep 10
	@echo "🔍 Checking service health..."
	make health
	@echo "✅ System ready!"
	@echo "🌐 Access the application at:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"