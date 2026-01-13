"""Integration tests for API endpoints."""
from fastapi.testclient import TestClient


def test_root_endpoint(test_client: TestClient):
    """Test root endpoint returns basic info."""
    response = test_client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["app"] == "hexapod-robot"
    assert data["version"] == "2.0.0"
    assert "environment" in data
    assert "robot" in data
    assert data["status"] == "running"


def test_health_check_endpoint(test_client: TestClient):
    """Test health check endpoint."""
    response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "robot" in data
    assert "version" in data
    assert "camera_enabled" in data
    assert "imu_enabled" in data
    assert "ultrasonic_enabled" in data


def test_metrics_endpoint(test_client: TestClient):
    """Test metrics endpoint exists."""
    response = test_client.get("/metrics")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "metrics" in data


def test_cors_headers(test_client: TestClient):
    """Test CORS headers are present."""
    response = test_client.get("/", headers={"Origin": "http://localhost:3000"})
    
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers
