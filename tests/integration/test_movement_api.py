"""Integration tests for movement API endpoints."""
from fastapi.testclient import TestClient


def test_move_endpoint(test_client: TestClient):
    """Test move robot endpoint."""
    payload = {
        "mode": "motion",
        "x": 10,
        "y": 5,
        "speed": 7,
        "angle": 0
    }
    
    response = test_client.post("/api/v1/movement/move", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "message" in data
    assert "command" in data
    assert "timestamp" in data


def test_move_endpoint_validation(test_client: TestClient):
    """Test move endpoint with invalid parameters."""
    # Speed too high
    payload = {
        "mode": "motion",
        "x": 10,
        "y": 5,
        "speed": 50,  # Max is 10
        "angle": 0
    }
    
    response = test_client.post("/api/v1/movement/move", json=payload)
    assert response.status_code == 422  # Validation error


def test_stop_endpoint(test_client: TestClient):
    """Test stop robot endpoint."""
    response = test_client.post("/api/v1/movement/stop")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["message"] == "Robot stopped successfully"


def test_attitude_endpoint(test_client: TestClient):
    """Test attitude control endpoint."""
    payload = {
        "roll": 5,
        "pitch": -3,
        "yaw": 0
    }
    
    response = test_client.post("/api/v1/movement/attitude", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["roll"] == 5
    assert data["data"]["pitch"] == -3
    assert data["data"]["yaw"] == 0


def test_position_endpoint(test_client: TestClient):
    """Test position control endpoint."""
    payload = {
        "x": 10,
        "y": 5,
        "z": -10
    }
    
    response = test_client.post("/api/v1/movement/position", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["x"] == 10
    assert data["data"]["y"] == 5
    assert data["data"]["z"] == -10


def test_movement_status_endpoint(test_client: TestClient):
    """Test movement status endpoint."""
    response = test_client.get("/api/v1/movement/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "moving" in data
    assert "current_speed" in data
    assert "current_position" in data
    assert "current_attitude" in data
