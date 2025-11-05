"""Integration tests for REST API server."""
import pytest
from fastapi.testclient import TestClient
from src.server.api_server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_mode" in data


def test_get_config(client):
    """Test configuration endpoint."""
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert "model_mode" in data
    assert "analysis" in data


def test_get_all_prompts(client):
    """Test getting all prompts."""
    response = client.get("/api/v1/prompts")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "prompts" in data


def test_get_specific_prompt(client):
    """Test getting specific prompt."""
    response = client.get("/api/v1/prompts/emotion_analysis")
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert "template" in data


def test_get_nonexistent_prompt(client):
    """Test getting non-existent prompt returns 404."""
    response = client.get("/api/v1/prompts/does_not_exist")
    assert response.status_code == 404


def test_get_available_modes(client):
    """Test getting available modes."""
    response = client.get("/api/v1/modes")
    assert response.status_code == 200
    data = response.json()
    assert "modes" in data
