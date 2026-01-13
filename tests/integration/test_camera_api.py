"""Integration tests for camera API endpoints."""
from fastapi.testclient import TestClient


def test_camera_rotate_endpoint(test_client: TestClient):
    """Test camera rotation endpoint."""
    payload = {
        "horizontal": 45,
        "vertical": -20
    }
    
    response = test_client.post("/api/v1/camera/rotate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["horizontal"] == 45
    assert data["data"]["vertical"] == -20


def test_camera_config_get(test_client: TestClient):
    """Test get camera configuration."""
    response = test_client.get("/api/v1/camera/config")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "enabled" in data
    assert "fps" in data
    assert "resolution" in data
