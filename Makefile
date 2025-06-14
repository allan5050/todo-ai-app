# Makefile for Todo AI App

# ==============================================================================
# Variables
# ==============================================================================

# Get the operating system
UNAME_S := $(shell uname -s)

# Backend variables
BACKEND_DIR := backend
BACKEND_VENV := $(BACKEND_DIR)/venv
BACKEND_PIP := $(BACKEND_VENV)/bin/pip
BACKEND_PYTHON := $(BACKEND_VENV)/bin/python
BACKEND_PYTEST := $(BACKEND_VENV)/bin/pytest

# Frontend variables
FRONTEND_DIR := frontend

# Windows specific adjustments
ifeq ($(UNAME_S),Windows_NT)
    BACKEND_PIP := $(BACKEND_VENV)/Scripts/pip
    BACKEND_PYTHON := $(BACKEND_VENV)/Scripts/python
    BACKEND_PYTEST := $(BACKEND_VENV)/Scripts/pytest
endif

# ==============================================================================
# High-Level Commands
# ==============================================================================

.PHONY: help install run clean test

help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  install          Install all backend and frontend dependencies"
	@echo "  run              Run both backend and frontend services (requires two terminals)"
	@echo "  run-backend      Run the backend server"
	@echo "  run-frontend     Run the frontend development server"
	@echo "  docker-up        Start the application using Docker Compose"
	@echo "  docker-down      Stop the application using Docker Compose"
	@echo "  test-backend     Run backend tests with pytest"
	@echo "  clean            Remove all generated files (venv, node_modules, etc.)"
	@echo "  lint             Run linters on both backend and frontend"


install: install-backend install-frontend
	@echo "✅ All dependencies installed."

run:
	@echo "Running both backend and frontend. Use two separate terminals."
	@echo "Terminal 1: make run-backend"
	@echo "Terminal 2: make run-frontend"

clean: clean-backend clean-frontend
	@echo "🧼 Project cleaned."

test: test-backend
	@echo "✅ All tests passed."
	
lint: lint-backend lint-frontend
	@echo "✅ Linting complete."

# ==============================================================================
# Docker Commands
# ==============================================================================

.PHONY: docker-up docker-down

docker-up:
	@echo "🐳 Starting application with Docker Compose..."
	docker-compose up --build

docker-down:
	@echo "Stopping application..."
	docker-compose down

# ==============================================================================
# Backend Commands
# ==============================================================================

.PHONY: install-backend run-backend test-backend clean-backend lint-backend

install-backend:
	@echo "Installing backend dependencies..."
	@if [ ! -d "$(BACKEND_VENV)" ]; then $(shell python -m venv $(BACKEND_VENV)); fi
	$(BACKEND_PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "Backend dependencies installed."

run-backend:
	@echo "🚀 Starting backend server at http://localhost:8000"
	$(BACKEND_PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir $(BACKEND_DIR)

test-backend:
	@echo "🧪 Running backend tests..."
	$(BACKEND_PYTEST) -v $(BACKEND_DIR)/tests
	@echo "Backend tests finished."

clean-backend:
	@echo "Cleaning backend..."
	rm -rf $(BACKEND_VENV)
	rm -rf $(BACKEND_DIR)/__pycache__
	rm -rf $(BACKEND_DIR)/.pytest_cache
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} +
	find $(BACKEND_DIR) -type f -name "*.pyc" -delete

lint-backend:
	@echo "Linting backend..."
	$(BACKEND_PIP) install black flake8
	$(BACKEND_PYTHON) -m black $(BACKEND_DIR)
	$(BACKEND_PYTHON) -m flake8 $(BACKEND_DIR)


# ==============================================================================
# Frontend Commands
# ==============================================================================

.PHONY: install-frontend run-frontend clean-frontend lint-frontend

install-frontend:
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "Frontend dependencies installed."

run-frontend:
	@echo "🚀 Starting frontend server at http://localhost:3000"
	cd $(FRONTEND_DIR) && npm start

clean-frontend:
	@echo "Cleaning frontend..."
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -rf $(FRONTEND_DIR)/build

lint-frontend:
	@echo "Linting frontend..."
	cd $(FRONTEND_DIR) && npm run lint && npm run format 