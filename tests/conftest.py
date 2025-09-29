"""
Shared test fixtures and configuration for all tests
"""
import pytest
import numpy as np
import sys
import os

# Add the project root to Python path so tests can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import fixtures from fixtures directory
from tests.fixtures.conftest import *

@pytest.fixture(scope="session")
def test_data_dir():
    """Directory for test data files."""
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'data')

@pytest.fixture(scope="session") 
def temp_test_dir(tmp_path_factory):
    """Temporary directory for test outputs."""
    return tmp_path_factory.mktemp("meeting_coach_tests")

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "requires_ollama: Tests that require Ollama to be running"
    )
    config.addinivalue_line(
        "markers", "requires_audio: Tests that require audio hardware"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on path."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration directory  
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            
        # Add slow marker to integration tests by default
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.slow)