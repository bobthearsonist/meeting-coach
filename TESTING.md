# Testing Infrastructure

The Teams Meeting Coach project uses a comprehensive testing infrastructure following Python best practices with pytest.

## Test Structure

```text
tests/
├── __init__.py
├── conftest.py                 # Shared test configuration and fixtures
├── fixtures/
│   ├── conftest.py            # Test fixtures and utilities
│   └── test_capture.wav       # Real audio file for testing
├── unit/                      # Fast unit tests
│   ├── __init__.py
│   ├── test_analyzer.py       # CommunicationAnalyzer tests
│   ├── test_transcriber.py    # Transcriber tests
│   └── test_dashboard.py      # Dashboard and timeline tests
└── integration/               # Slower integration tests
    ├── __init__.py
    ├── test_pipeline.py       # End-to-end pipeline tests
    ├── test_real_audio_integration.py      # Console app integration
    └── test_real_audio_functionality.py    # Real audio file tests
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **Fast execution** (< 1 second each)
- **No external dependencies** (no Ollama, no audio hardware)
- **Isolated component testing**
- Use mocking for external services
- Test individual functions and classes

### Integration Tests (`tests/integration/`)

- **End-to-end workflows**
- **Real component interaction**
- **External dependency testing**
- May require Ollama, audio hardware, or real files

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.slow` - Tests that take > 5 seconds
- `@pytest.mark.requires_ollama` - Tests needing Ollama server
- `@pytest.mark.requires_audio` - Tests needing audio hardware

## Running Tests

### Quick Test Commands

```bash
# Run all tests
make test

# Run only fast unit tests
make test-unit

# Run integration tests
make test-integration

# Run tests without slow external dependencies
make test-fast
```

### Specific Test Categories

```bash
# Tests requiring Ollama (will skip if not available)
make test-requires-ollama

# Tests requiring audio hardware
make test-requires-audio

# Tests using real audio files
make test-real-audio

# Test specific components
make test-analyzer
make test-transcriber
make test-dashboard
```

### Coverage and Quality

```bash
# Run tests with coverage report
make test-coverage

# Run code linting
make lint

# Format code
make format
```

### Direct pytest Commands

```bash
# Run specific test file
pytest tests/unit/test_analyzer.py -v

# Run tests matching pattern
pytest tests/ -k "test_audio" -v

# Run with specific markers
pytest tests/ -m "unit and not slow" -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Test Fixtures

### Audio Data Fixtures

- `sample_audio_data` - Synthetic audio for testing transcription
- `sample_transcription_results` - Mock transcription outputs
- `test_audio_file` - Path to real test audio file

### Analysis Fixtures

- `communication_analysis_test_cases` - Test cases for tone analysis
- `dashboard_scenarios` - Dashboard testing scenarios
- `MockOllamaResponse` - Mock Ollama API responses

### Configuration Fixtures

- `temp_test_dir` - Temporary directory for test outputs
- `test_data_dir` - Directory containing test data files

## Real Audio Testing

The project includes tests that use a real audio file (`test_capture.wav`) for more realistic testing:

### Creating Test Audio

```bash
# Generate test audio file by recording 5 seconds
make create-test-audio
# or
python main.py --test-audio
```

### Audio File Tests

- **Transcription accuracy** with real speech
- **Filler word detection** on actual recordings  
- **Speaking pace analysis** with real timing
- **Complete pipeline** from audio → transcription → analysis

## Mocking Strategy

### External Services

- **Ollama API calls** are mocked in unit tests
- **Real Ollama testing** available in integration tests with `@pytest.mark.requires_ollama`
- **Audio hardware** mocked in unit tests, real testing with `@pytest.mark.requires_audio`

### Example Mock Usage

```python
@patch('analyzer.ollama.chat')
def test_analyzer_with_mock_ollama(mock_chat, analyzer):
    mock_response = {
        'message': {
            'content': '{"tone": "supportive", "confidence": 0.8}'
        }
    }
    mock_chat.return_value = mock_response
    
    result = analyzer.analyze("Test text")
    assert result['tone'] == 'supportive'
```

## Test Data Management

### Synthetic Data

- Generated in test fixtures for consistent, repeatable testing
- No external dependencies
- Fast execution

### Real Data

- `test_capture.wav` for realistic audio testing
- Optional - tests skip if not available
- Provides validation against real-world scenarios

## Continuous Integration

### Development Workflow

```bash
# Quick tests during development
make dev-test

# Full CI test suite
make ci-test
```

### Test Selection Strategy

1. **Development**: Run `make test-fast` (< 10 seconds)
2. **Pre-commit**: Run `make test-unit` (< 30 seconds)  
3. **CI Pipeline**: Run `make test` (full suite)
4. **Release**: Run `make ci-test` (with coverage)

## Autism/ADHD Specific Testing

The project includes specialized tests for autism and ADHD coaching scenarios:

### Scenario Testing

- **Elevated/excited states** (ADHD hyperfocus)
- **Interrupting patterns**
- **Special interest domination**
- **Overwhelmed/shutdown responses**
- **Repetitive speech patterns**

### Emotion Analysis Accuracy

- **False positive testing** with neutral content
- **True positive validation** with problematic content
- **Confidence threshold testing**

## Performance Testing

### Benchmarks

- **Transcription speed** vs. audio duration
- **Memory usage** during processing
- **Response time** for analysis

### Realistic Testing

- **5-second audio chunks** (typical meeting segments)
- **Speaking pace analysis** (WPM calculations)
- **Real-time processing** simulation

## Debugging and Development

### Debug Helpers

```bash
# Check audio devices
make debug-audio

# Test transcription with existing file
make debug-transcription

# Validate setup
make check-deps
```

### Test Development Tips

1. **Start with unit tests** - Fast feedback loop
2. **Use fixtures** - Consistent test data
3. **Mock external dependencies** - Reliable testing
4. **Add integration tests** - Real-world validation
5. **Use appropriate markers** - Selective test execution

## Common Issues and Solutions

### Audio Tests Failing
- Ensure audio hardware is available: `make debug-audio`
- Create test audio file: `make create-test-audio`
- Skip audio tests: `pytest tests/ -m "not requires_audio"`

### Ollama Tests Failing  
- Install and start Ollama server
- Configure correct model in `config.py`
- Skip Ollama tests: `pytest tests/ -m "not requires_ollama"`

### Slow Test Execution
- Run only fast tests: `make test-fast`
- Use specific markers: `pytest tests/ -m "unit"`
- Check for blocking operations in unit tests

This testing infrastructure ensures reliable, maintainable, and comprehensive test coverage while supporting efficient development workflows.