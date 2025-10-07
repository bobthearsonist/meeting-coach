# Makefile for Meeting Coach project

.PHONY: help install test test-unit test-integration test-fast test-coverage clean lint format docs run-demos run-server run-console run run-with-logs stop logs

# Default target
help:
	@echo "Teams Meeting Coach - Development Commands"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  run                  - Start with dashboard (logs to file)"
	@echo "  run-server           - Start Meeting Coach engine only"
	@echo "  run-console          - Start console dashboard only (server must be running)"
	@echo "  run-with-logs        - Start with separate terminal windows"
	@echo "  stop                 - Stop background Meeting Coach process"
	@echo "  logs                 - View Meeting Coach logs in real-time"
	@echo ""
	@echo "📦 Installation:"
	@echo "  install              - Install dependencies"
	@echo "  install-dev          - Install dev dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test                 - Run all tests"
	@echo "  test-unit            - Run unit tests only"
	@echo "  test-integration     - Run integration tests only"
	@echo "  test-fast            - Run fast tests only (no slow/external deps)"
	@echo "  test-slow            - Run slow tests only"
	@echo "  test-requires-ollama - Run tests that require Ollama"
	@echo "  test-requires-audio  - Run tests that require audio hardware"
	@echo "  test-real-audio      - Run tests with real audio files"
	@echo "  test-coverage        - Run tests with coverage reporting"
	@echo ""
	@echo "🎨 Development:"
	@echo "  lint                 - Run code linting"
	@echo "  format               - Format code"
	@echo "  clean                - Clean up temporary files"

# Python executable (uses root venv)
PYTHON := $(shell if [ -d "../venv" ]; then echo "../venv/bin/python"; else echo "python3"; fi)
PIP := $(shell if [ -d "../venv" ]; then echo "../venv/bin/pip"; else echo "pip3"; fi)

# Install dependencies
install:
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install black flake8 mypy isort

# WebSocket Server Commands
run-server:
	@echo "🚀 Starting Meeting Coach Engine with WebSocket server on ws://localhost:3001"
	@echo "Press Ctrl+C to stop"
	$(PYTHON) main.py

run-console:
	@echo "🖥️  Starting console client dashboard"
	@echo "💡 Make sure the server is already running (make run-server)"
	@echo "Press Ctrl+C to stop"
	$(PYTHON) -m src.server.console_client

run:
	@echo "🚀 Starting Teams Meeting Coach"
	@echo "📝 Server logs will be written to: meeting-coach.log"
	@echo "📊 Dashboard will appear below..."
	@echo ""
	@sleep 1
	@($(PYTHON) main.py > meeting-coach.log 2>&1 & echo $$! > .meeting-coach.pid; \
		sleep 3; \
		$(PYTHON) -m src.server.console_client; \
		kill $$(cat .meeting-coach.pid) 2>/dev/null || true; \
		rm -f .meeting-coach.pid)

run-with-logs:
	@echo "🚀 Starting Teams Meeting Coach"
	@echo "Server: ws://localhost:3001"
	@echo ""
	@echo "Opening two terminal windows:"
	@echo "1. Meeting Coach Engine + WebSocket Server"
	@echo "2. Console Client Dashboard"
	@echo ""
	@osascript -e 'tell application "Terminal"' \
		-e 'do script "cd $(PWD) && $(PYTHON) main.py"' \
		-e 'delay 3' \
		-e 'do script "cd $(PWD) && $(PYTHON) -m src.server.console_client"' \
		-e 'end tell'
	@echo "✅ Terminals opened! Press Ctrl+C in either window to stop both."

stop:
	@echo "🛑 Stopping Meeting Coach..."
	@kill $$(cat .meeting-coach.pid) 2>/dev/null || echo "No running instance found"
	@rm -f .meeting-coach.pid
	@echo "✅ Stopped"

logs:
	@echo "📝 Viewing Meeting Coach logs (Ctrl+C to exit)..."
	@tail -f meeting-coach.log

# Test targets
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v -m "unit"

test-integration:
	pytest tests/integration/ -v -m "integration"

test-fast:
	pytest tests/ -v -m "not slow"

test-slow:
	pytest tests/ -v -m "slow"

test-requires-ollama:
	pytest tests/ -v -m "requires_ollama"

test-requires-audio:
	pytest tests/ -v -m "requires_audio"

test-real-audio:
	pytest tests/integration/test_real_audio_functionality.py -v

test-coverage:
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Test specific components
test-analyzer:
	pytest tests/unit/test_analyzer.py -v

test-transcriber:
	pytest tests/unit/test_transcriber.py -v

test-dashboard:
	pytest tests/unit/test_dashboard.py -v

test-pipeline:
	pytest tests/integration/test_pipeline.py -v

# Our new comprehensive test suite
test-comprehensive:
	@echo "Running comprehensive test suite..."
	@echo "✅ Unit Tests: CommunicationAnalyzer (40 tests)"
	pytest tests/unit/test_analyzer.py -v
	@echo ""
	@echo "✅ Unit Tests: AudioCapture (24 tests)"
	pytest tests/unit/test_audio_capture.py -v
	@echo ""
	@echo "✅ Integration Tests: Full Pipeline (6 tests)"
	pytest tests/integration/test_full_pipeline.py -v
	@echo ""
	@echo "🎉 Comprehensive test suite complete!"

test-new:
	@echo "Running our newly created comprehensive tests..."
	pytest tests/unit/test_analyzer.py tests/unit/test_audio_capture.py tests/integration/test_full_pipeline.py -v

# Demos
run-demos:
	@echo "Running dashboard demo..."
	python demos/dashboard_demo.py
	@echo ""
	@echo "Running colors demo..."
	python demos/colors_demo.py
	@echo ""
	@echo "Running visual interface demo..."
	python demos/visual_interface_demo.py

# Code quality
lint:
	@echo "Running pylint..."
	pylint *.py --disable=C0103,C0114,C0115,C0116,R0903,R0912,R0915 || true
	@echo "Running flake8..."
	flake8 *.py --max-line-length=100 --ignore=E501,W503 || true

format:
	@echo "Formatting code with black..."
	black *.py tests/ demos/ --line-length=100
	@echo "Sorting imports with isort..."
	isort *.py tests/ demos/ --profile=black

# Create test audio file
create-test-audio:
	$(PYTHON) main.py --test-audio

# Debug helpers
debug-audio:
	$(PYTHON) main.py --select-device

debug-transcription:
	$(PYTHON) main.py --test-transcription

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/

# Development workflow helpers
dev-test: test-unit test-fast
	@echo "✅ Quick development tests completed"

ci-test: install test-coverage lint
	@echo "✅ Full CI test suite completed"

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "TODO: Add documentation generation"

# Development helpers
dev-install: install
	pip install black isort pylint flake8

setup-dev: dev-install
	@echo "Development environment setup complete!"
	@echo "Run 'make test-fast' to verify everything works."

# CI targets (using first definition from line 182)
# ci-test: install test-coverage lint (defined above)

ci-full-test:
	python run_tests.py all --coverage
