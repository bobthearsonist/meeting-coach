# Makefile for Meeting Coach project

.PHONY: help install test test-unit test-integration test-fast test-coverage clean lint format docs run-demos

# Default target
help:
	@echo "Teams Meeting Coach - Test Management"
	@echo ""
	@echo "Available targets:"
	@echo "  install              - Install dependencies"
	@echo "  test                 - Run all tests"
	@echo "  test-unit            - Run unit tests only"
	@echo "  test-integration     - Run integration tests only"
	@echo "  test-fast            - Run fast tests only (no slow/external deps)"
	@echo "  test-slow            - Run slow tests only"
	@echo "  test-requires-ollama - Run tests that require Ollama"
	@echo "  test-requires-audio  - Run tests that require audio hardware"
	@echo "  test-real-audio      - Run tests with real audio files"
	@echo "  test-coverage        - Run tests with coverage reporting"
	@echo "  run-demos            - Run demonstration scripts"
	@echo "  lint                 - Run code linting"
	@echo "  format               - Format code"
	@echo "  check-deps           - Check dependencies and setup"
	@echo "  create-test-audio    - Create test audio file"
	@echo "  clean                - Clean up temporary files"

# Install dependencies
install:
	pip install -r requirements.txt

install-dev: install
	pip install black flake8 mypy isort

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

# Setup validation
check-deps:
	python setup_check.py

# Create test audio file
create-test-audio:
	python main.py --test-audio

# Debug helpers
debug-audio:
	python main.py --select-device

debug-transcription:
	python main.py --test-transcription

# Clean up
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf tests/unit/__pycache__/
	rm -rf tests/integration/__pycache__/
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Development workflow helpers
dev-test: test-unit test-fast
	@echo "✅ Quick development tests completed"

ci-test: install test-coverage lint
	@echo "✅ Full CI test suite completed"

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/

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

# CI targets
ci-test:
	python run_tests.py --fast --coverage

ci-full-test:
	python run_tests.py all --coverage
