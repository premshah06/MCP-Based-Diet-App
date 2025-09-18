# Diet Coach MCP - Development Makefile

.PHONY: help test test-fast test-api test-mcp install-deps lint clean build up down logs health

# Default target
help:
	@echo "Diet Coach MCP - Available Commands:"
	@echo ""
	@echo "Development & Testing:"
	@echo "  make install-deps    Install all dependencies"
	@echo "  make test           Run all tests with coverage"
	@echo "  make test-fast      Run tests excluding slow ones"
	@echo "  make test-api       Run only FastAPI tests"
	@echo "  make test-mcp       Run only MCP server tests"
	@echo "  make lint           Run linting on all components"
	@echo "  make clean          Clean up test artifacts"
	@echo ""
	@echo "Docker Operations:"
	@echo "  make build          Build Docker images"
	@echo "  make up             Start all services"
	@echo "  make down           Stop all services"
	@echo "  make logs           Show service logs"
	@echo "  make health         Check service health"
	@echo ""
	@echo "Monitoring:"
	@echo "  make watch          Start health monitoring"
	@echo "  make restart-unhealthy  Restart any unhealthy services"

# Development commands
install-deps:
	@echo "Installing dependencies for all components..."
	python test_runner.py --install-deps --component all

test:
	@echo "Running all tests with coverage..."
	python test_runner.py --coverage --lint

test-fast:
	@echo "Running fast tests only..."
	python test_runner.py --fast --coverage

test-api:
	@echo "Running FastAPI tests..."
	python test_runner.py --component api --coverage

test-mcp:
	@echo "Running MCP server tests..."
	python test_runner.py --component mcp --coverage

lint:
	@echo "Running linting on all components..."
	python test_runner.py --lint --component all

clean:
	@echo "Cleaning up test artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

# Docker commands
build:
	@echo "Building Docker images..."
	cd docker && docker compose build

up:
	@echo "Starting all services..."
	cd docker && docker compose up -d

down:
	@echo "Stopping all services..."
	cd docker && docker compose down

logs:
	@echo "Showing service logs..."
	cd docker && docker compose logs -f

health:
	@echo "Checking service health..."
	cd docker && docker compose ps

# Monitoring commands
watch:
	@echo "Starting health monitoring..."
	./docker/restart_watch.sh

restart-unhealthy:
	@echo "Checking and restarting unhealthy services..."
	./docker/restart_watch.sh --check-once

# Development workflow shortcuts
dev-setup: install-deps test
	@echo "Development setup complete!"

dev-test: test-fast lint
	@echo "Quick development test complete!"

deploy-ready: clean test build
	@echo "Application is ready for deployment!"

# API testing shortcuts
test-tdee:
	python test_runner.py --component api --test-pattern "test_tdee"

test-mealplan:
	python test_runner.py --component api --test-pattern "test_meal_plan"

test-explain:
	python test_runner.py --component api --test-pattern "test_explain"

# MCP testing shortcuts
test-mcp-tools:
	python test_runner.py --component mcp --test-pattern "test_tool"

test-mcp-resources:
	python test_runner.py --component mcp --test-pattern "test_resource"
