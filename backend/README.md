# Meeting Coach Backend

Python backend and console application for Teams Meeting Coach - real-time emotional monitoring for neurodivergent individuals.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
```

## Usage

```bash
# Run the console application
python main.py

# Run with virtual environment helper
./run_with_venv.sh
```

## Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run fast tests (no slow/external deps)
make test-fast

# Run with coverage
make test-coverage
```

## Development

```bash
# Install dev dependencies
make install-dev

# Format code
make format

# Lint code
make lint

# Run demos
make run-demos
```

## Available Make Targets

Run `make help` to see all available commands.

## Structure

```
backend/
├── analyzer.py              # Communication analysis
├── audio_capture.py         # Audio input handling
├── transcriber.py           # Speech-to-text
├── dashboard.py             # Console UI
├── main.py                  # Main entry point
├── tests/                   # Test suite
└── demos/                   # Demo applications
```
