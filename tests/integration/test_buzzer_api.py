"""Integration tests for buzzer API endpoints."""
from fastapi.testclient import TestClient


def test_buzzer_beep_endpoint(test_client: TestClient):
    """Test buzzer beep."""
    payload = {
        "enabled": True,
        "duration": 0.5
    }
    
    response = test_client.post("/api/v1/buzzer/beep", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["enabled"] is True


def test_buzzer_off_endpoint(test_client: TestClient):
    """Test buzzer off."""
    payload = {
        "enabled": False
    }
    
    response = test_client.post("/api/v1/buzzer/beep", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["enabled"] is False
