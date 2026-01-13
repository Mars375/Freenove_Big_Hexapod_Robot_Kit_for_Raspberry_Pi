"""Integration tests for LEDs API endpoints."""
from fastapi.testclient import TestClient


def test_led_mode_endpoint(test_client: TestClient):
    """Test LED mode setting."""
    payload = {
        "mode": "solid",
        "color": {
            "red": 255,
            "green": 0,
            "blue": 0
        }
    }
    
    response = test_client.post("/api/v1/leds/mode", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["mode"] == "solid"


def test_led_color_endpoint(test_client: TestClient):
    """Test LED color setting."""
    payload = {
        "red": 0,
        "green": 255,
        "blue": 0
    }
    
    response = test_client.post("/api/v1/leds/color", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
