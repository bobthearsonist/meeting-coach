# Teams Meeting Coach - Monorepo Makefile
# Orchestrates both backend (Python) and frontend (React Native)

.PHONY: help install test clean dev

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)   Teams Meeting Coach - Monorepo Commands$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Installation:$(NC)"
	@echo "  make install             - Install both backend and frontend"
	@echo "  make backend-install     - Install backend dependencies only"
	@echo "  make frontend-install    - Install frontend dependencies only"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev                 - Start both backend and frontend in dev mode"
	@echo "  make backend-dev         - Run backend console application"
	@echo "  make frontend-dev        - Start frontend Metro bundler"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test                - Run all tests (backend + frontend)"
	@echo "  make backend-test        - Run backend tests only"
	@echo "  make frontend-test       - Run frontend tests only"
	@echo "  make test-fast           - Run fast backend tests"
	@echo "  make test-coverage       - Run backend tests with coverage"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make lint                - Lint all code (backend + frontend)"
	@echo "  make format              - Format all code (backend + frontend)"
	@echo "  make backend-lint        - Lint backend code"
	@echo "  make frontend-lint       - Lint frontend code"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean               - Clean all temporary files"
	@echo "  make backend-clean       - Clean backend files"
	@echo "  make frontend-clean      - Clean frontend files"
	@echo ""
	@echo "$(GREEN)Project Info:$(NC)"
	@echo "  make status              - Show project structure and status"
	@echo ""
	@echo "$(YELLOW)Tip: You can also use Make commands directly in backend/ or frontend/$(NC)"

# ═══════════════════════════════════════════════════════════
# Installation
# ═══════════════════════════════════════════════════════════

install: backend-install frontend-install
	@echo "$(GREEN)✓ Installation complete!$(NC)"

backend-install:
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && make install
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

frontend-install:
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

# ═══════════════════════════════════════════════════════════
# Development
# ═══════════════════════════════════════════════════════════

dev:
	@echo "$(YELLOW)Starting development environment...$(NC)"
	@echo "$(YELLOW)Note: This will start both backend and frontend.$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop.$(NC)"
	@echo ""
	@make -j2 backend-dev frontend-dev

backend-dev:
	@echo "$(BLUE)Starting backend console application...$(NC)"
	cd backend && python main.py

frontend-dev:
	@echo "$(BLUE)Starting frontend Metro bundler...$(NC)"
	cd frontend && npm start

# ═══════════════════════════════════════════════════════════
# Testing
# ═══════════════════════════════════════════════════════════

test: backend-test frontend-test
	@echo "$(GREEN)✓ All tests completed!$(NC)"

backend-test:
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && make test

frontend-test:
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test

test-fast:
	@echo "$(BLUE)Running fast backend tests...$(NC)"
	cd backend && make test-fast

test-coverage:
	@echo "$(BLUE)Running backend tests with coverage...$(NC)"
	cd backend && make test-coverage

# ═══════════════════════════════════════════════════════════
# Code Quality
# ═══════════════════════════════════════════════════════════

lint: backend-lint frontend-lint
	@echo "$(GREEN)✓ All linting complete!$(NC)"

backend-lint:
	@echo "$(BLUE)Linting backend code...$(NC)"
	cd backend && make lint

frontend-lint:
	@echo "$(BLUE)Linting frontend code...$(NC)"
	cd frontend && npm run lint

format: backend-format frontend-format
	@echo "$(GREEN)✓ All code formatted!$(NC)"

backend-format:
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && make format

frontend-format:
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format

# ═══════════════════════════════════════════════════════════
# Cleanup
# ═══════════════════════════════════════════════════════════

clean: backend-clean frontend-clean
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

backend-clean:
	@echo "$(BLUE)Cleaning backend...$(NC)"
	cd backend && make clean

frontend-clean:
	@echo "$(BLUE)Cleaning frontend...$(NC)"
	cd frontend && rm -rf node_modules
	cd frontend && rm -rf .metro

# ═══════════════════════════════════════════════════════════
# Project Info
# ═══════════════════════════════════════════════════════════

status:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)   Teams Meeting Coach - Project Status$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Project Structure:$(NC)"
	@echo "├── backend/          Python console application & analysis engine"
	@echo "├── frontend/         React Native UI"
	@echo "├── docs/             Documentation"
	@echo "└── README.md         Project overview"
	@echo ""
	@echo "$(GREEN)Backend Status:$(NC)"
	@if [ -d "backend/venv" ]; then \
		echo "  ✓ Virtual environment: $(GREEN)exists$(NC)"; \
	else \
		echo "  ✗ Virtual environment: $(YELLOW)not found$(NC) (run 'make backend-install')"; \
	fi
	@echo ""
	@echo "$(GREEN)Frontend Status:$(NC)"
	@if [ -d "frontend/node_modules" ]; then \
		echo "  ✓ Node modules: $(GREEN)installed$(NC)"; \
	else \
		echo "  ✗ Node modules: $(YELLOW)not installed$(NC) (run 'make frontend-install')"; \
	fi
	@echo ""
	@echo "$(YELLOW)Run 'make help' for available commands$(NC)"
