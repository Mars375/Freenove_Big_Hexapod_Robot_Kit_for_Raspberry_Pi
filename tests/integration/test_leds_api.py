"""Integration tests for LEDs API endpoints."""
from fastapi.testclient import TestClient


def test_led_color_endpoint(test_client: TestClient):
    """Test LED color setting."""
    payload = {
        "r": 0,
        "g": 255,
        "b": 0
    }
    
    response = test_client.post("/api/v1/leds/color", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True


def test_led_brightness_endpoint(test_client: TestClient):
    """Test LED brightness setting."""
    payload = {"brightness": 128}
    
    response = test_client.post("/api/v1/leds/brightness", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["brightness"] == 128


def test_led_rainbow_endpoint(test_client: TestClient):
    """Test LED rainbow animation."""
    payload = {"iterations": 2}

    response = test_client.post("/api/v1/leds/rainbow", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["iterations"] == 2


def test_led_off_endpoint(test_client: TestClient):
    """Test turning off LEDs."""
    response = test_client.post("/api/v1/leds/off")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True


def test_led_status_endpoint(test_client: TestClient):
    """Test getting LED status."""
    response = test_client.get("/api/v1/leds/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "led_count" in data["data"]
    assert "brightness" in data["data"]
    assert "status" in data["data"]
