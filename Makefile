# Teams Meeting Coach - Monorepo Makefile
# Orchestrates both backend (Python) and frontend (React Native)

.PHONY: help install test clean run backend frontend metro macos stop

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
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
	@echo "  make run                 - 🚀 Start full dev environment with overmind"
	@echo "  make run backend         - Run backend WebSocket server only"
	@echo "  make run metro           - Run Metro bundler (JS bundler) only"
	@echo "  make run macos           - Launch macOS app (requires Metro running)"
	@echo ""
	@echo "$(GREEN)Overmind Process Control:$(NC)"
	@echo "  overmind connect backend - Attach to backend process logs"
	@echo "  overmind connect metro   - Attach to Metro bundler logs"
	@echo "  overmind connect macos   - Attach to macOS app logs"
	@echo "  overmind restart macos   - Restart just the app"
	@echo "  overmind restart backend - Restart backend without stopping others"
	@echo "  overmind restart metro   - Restart Metro without stopping others"
	@echo "  Ctrl+C (in overmind)     - Stop all processes"
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
	@echo "  make lint-check          - Lint with warnings as errors (CI mode)"
	@echo "  make format              - Format all code (backend + frontend)"
	@echo "  make format-check        - Check formatting without modifying files"
	@echo "  make backend-lint        - Lint backend code"
	@echo "  make frontend-lint       - Lint frontend code"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean               - Clean all temporary files"
	@echo "  make backend-clean       - Clean backend files"
	@echo "  make frontend-clean      - Clean frontend files"
	@echo "  make stop                - Stop all running services"
	@echo ""
	@echo "$(GREEN)Project Info:$(NC)"
	@echo "  make status              - Show project structure and status"
	@echo "  make check-ports         - Check if WebSocket ports are in use"
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
	@echo "$(BLUE)Using Node.js version from .nvmrc...$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm install; \
	else \
		cd frontend && npm install; \
	fi
	@echo "$(BLUE)Installing CocoaPods dependencies...$(NC)"
	cd frontend/macos && pod install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

# ═══════════════════════════════════════════════════════════
# Development
# ═══════════════════════════════════════════════════════════

# New unified 'run' command with subcommands
run:
	@if [ "$(filter-out $@,$(MAKECMDGOALS))" = "" ]; then \
		$(MAKE) run-start; \
	elif [ "$(filter-out $@,$(MAKECMDGOALS))" = "backend" ]; then \
		$(MAKE) run-backend; \
	elif [ "$(filter-out $@,$(MAKECMDGOALS))" = "metro" ]; then \
		$(MAKE) run-metro; \
	elif [ "$(filter-out $@,$(MAKECMDGOALS))" = "frontend" ]; then \
		echo "$(YELLOW)💡 Hint: 'make run metro' is clearer (frontend → metro bundler)$(NC)"; \
		$(MAKE) run-metro; \
	elif [ "$(filter-out $@,$(MAKECMDGOALS))" = "macos" ]; then \
		$(MAKE) run-macos; \
	else \
		echo "$(RED)Usage: make run [backend|metro|macos]$(NC)"; \
		echo "$(YELLOW)  (no args) - Start full dev environment$(NC)"; \
		echo "$(YELLOW)  backend   - WebSocket server only$(NC)"; \
		echo "$(YELLOW)  metro     - JavaScript bundler only$(NC)"; \
		echo "$(YELLOW)  macos     - Launch macOS app$(NC)"; \
		exit 1; \
	fi

# Catch the subcommand arguments
backend frontend metro macos:
	@:

run-start:
	@echo "$(BLUE)🚀 Starting Teams Meeting Coach Development Environment$(NC)"
	@echo "$(GREEN)   Using overmind process manager$(NC)"
	@echo ""
	@if ! command -v overmind &> /dev/null; then \
		echo "$(RED)❌ overmind not found$(NC)"; \
		echo "$(YELLOW)Install with: brew install overmind$(NC)"; \
		echo ""; \
		echo "$(YELLOW)After installation, run 'make run' again$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Starting all services:$(NC)"
	@echo "  • Backend WebSocket server (port from .env)"
	@echo "  • Metro bundler (port from .env)"
	@echo "  • macOS app (auto-connects to Metro when ready)"
	@echo ""
	@echo "$(YELLOW)💡 Useful overmind commands:$(NC)"
	@echo "$(YELLOW)   overmind connect backend  - Attach to backend logs$(NC)"
	@echo "$(YELLOW)   overmind connect metro    - Attach to Metro logs$(NC)"
	@echo "$(YELLOW)   overmind connect macos    - Attach to app logs$(NC)"
	@echo "$(YELLOW)   overmind restart macos    - Restart just the app$(NC)"
	@echo "$(YELLOW)   Ctrl+C                    - Stop all services$(NC)"
	@echo ""
	overmind start

run-backend:
	@echo "$(BLUE)Starting backend WebSocket server...$(NC)"
	cd backend && python main.py

run-metro:
	@echo "$(BLUE)Starting Metro bundler (JavaScript bundler)...$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm start; \
	else \
		cd frontend && npm start; \
	fi

run-macos:
	@echo "$(BLUE)Launching React Native macOS app...$(NC)"
	@echo "$(YELLOW)💡 Metro bundler must be running first (make run metro)$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npx react-native run-macos --no-packager; \
	else \
		cd frontend && npx react-native run-macos --no-packager; \
	fi

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
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm test -- --passWithNoTests; \
	else \
		cd frontend && npm test -- --passWithNoTests; \
	fi

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

lint-check: backend-lint-check frontend-lint-check
	@echo "$(GREEN)✓ All lint checks passed (CI mode)!$(NC)"

backend-lint:
	@echo "$(BLUE)Linting backend code...$(NC)"
	cd backend && make lint

backend-lint-check:
	@echo "$(BLUE)Checking backend code (strict mode)...$(NC)"
	cd backend && make lint-check

frontend-lint:
	@echo "$(BLUE)Linting frontend code...$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm run lint; \
	else \
		cd frontend && npm run lint; \
	fi

frontend-lint-check:
	@echo "$(BLUE)Checking frontend code (strict mode)...$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm run lint:check; \
	else \
		cd frontend && npm run lint:check; \
	fi

format: backend-format frontend-format
	@echo "$(GREEN)✓ All code formatted!$(NC)"

format-check: backend-format-check frontend-format-check
	@echo "$(GREEN)✓ All code formatting is correct!$(NC)"

backend-format:
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && make format

backend-format-check:
	@echo "$(BLUE)Checking backend code formatting...$(NC)"
	cd backend && make format-check

frontend-format:
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm run format; \
	else \
		cd frontend && npm run format; \
	fi

frontend-format-check:
	@echo "$(BLUE)Checking frontend code formatting...$(NC)"
	@if command -v nvm >/dev/null 2>&1; then \
		cd frontend && nvm use && npm run format:check; \
	else \
		cd frontend && npm run format:check; \
	fi

# Combined pre-commit check
pre-commit: format-check lint-check
	@echo "$(GREEN)✅ Pre-commit checks passed!$(NC)"

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
	cd frontend/macos && rm -rf build
	cd frontend/macos && rm -rf Pods
	cd frontend/macos && rm -rf DerivedData
	@echo "$(YELLOW)Note: Run 'make frontend-install' to reinstall dependencies$(NC)"

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
	@if [ -d "frontend/macos/Pods" ]; then \
		echo "  ✓ CocoaPods: $(GREEN)installed$(NC)"; \
	else \
		echo "  ✗ CocoaPods: $(YELLOW)not installed$(NC) (run 'make frontend-install')"; \
	fi
	@if [ -f ".nvmrc" ]; then \
		echo "  ✓ Node version: $(GREEN)$(shell cat .nvmrc)$(NC)"; \
	else \
		echo "  ? Node version: $(YELLOW)no .nvmrc found$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Run 'make help' for available commands$(NC)"

check-ports:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)   Checking WebSocket Ports$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Port 3001 (Backend WebSocket Server):$(NC)"
	@if lsof -i :3001 >/dev/null 2>&1; then \
		echo "  ✓ $(GREEN)In use$(NC)"; \
		lsof -i :3001; \
	else \
		echo "  ✗ $(YELLOW)Available$(NC) (backend not running)"; \
	fi
	@echo ""
	@echo "$(GREEN)Python processes:$(NC)"
	@if ps aux | grep "python.*main.py" | grep -v grep >/dev/null 2>&1; then \
		echo "  ✓ $(GREEN)Backend running$(NC)"; \
		ps aux | grep "python.*main.py" | grep -v grep; \
	else \
		echo "  ✗ $(YELLOW)Backend not running$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)To start backend: make backend-dev$(NC)"
	@echo "$(YELLOW)To start full environment: make start$(NC)"

# Stop all running services
stop:
	@echo "$(YELLOW)🛑 Stopping all services...$(NC)"
	@# Load .env to get ports
	@if [ -f .env ]; then \
		export $$(cat .env | grep -v '^#' | xargs) && \
		WEBSOCKET_PORT=$${WEBSOCKET_PORT:-3002} && \
		METRO_PORT=$${METRO_PORT:-8082} && \
		echo "$(YELLOW)Checking for processes on port $$WEBSOCKET_PORT...$(NC)" && \
		if lsof -ti:$$WEBSOCKET_PORT >/dev/null 2>&1; then \
			lsof -ti:$$WEBSOCKET_PORT | xargs kill 2>/dev/null && \
			echo "$(GREEN)✅ Stopped backend on port $$WEBSOCKET_PORT$(NC)"; \
		else \
			echo "$(YELLOW)No process on port $$WEBSOCKET_PORT$(NC)"; \
		fi && \
		echo "$(YELLOW)Checking for processes on port $$METRO_PORT...$(NC)" && \
		if lsof -ti:$$METRO_PORT >/dev/null 2>&1; then \
			lsof -ti:$$METRO_PORT | xargs kill 2>/dev/null && \
			echo "$(GREEN)✅ Stopped Metro on port $$METRO_PORT$(NC)"; \
		else \
			echo "$(YELLOW)No process on port $$METRO_PORT$(NC)"; \
		fi; \
	else \
		echo "$(RED)No .env file found, using default ports$(NC)" && \
		lsof -ti:3002 | xargs kill 2>/dev/null || true && \
		lsof -ti:8082 | xargs kill 2>/dev/null || true; \
	fi
	@echo "$(GREEN)✅ Done$(NC)"
