"""Integration tests for sensors API endpoints."""
from fastapi.testclient import TestClient


def test_imu_endpoint(test_client: TestClient):
    """Test IMU sensor endpoint."""
    response = test_client.get("/api/v1/sensors/imu")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "accel_x" in data
    assert "accel_y" in data
    assert "accel_z" in data
    assert "gyro_x" in data
    assert "gyro_y" in data
    assert "gyro_z" in data


def test_ultrasonic_endpoint(test_client: TestClient):
    """Test ultrasonic sensor endpoint."""
    response = test_client.get("/api/v1/sensors/ultrasonic")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "distance" in data
    assert data["distance"] >= 0


def test_battery_endpoint(test_client: TestClient):
    """Test battery sensor endpoint."""
    response = test_client.get("/api/v1/sensors/battery")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "voltage" in data
    assert "percentage" in data
    assert "is_low" in data
    assert "is_critical" in data


def test_all_sensors_endpoint(test_client: TestClient):
    """Test all sensors combined endpoint."""
    response = test_client.get("/api/v1/sensors/all")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "imu" in data
    assert "ultrasonic" in data
    assert "battery" in data
    assert "timestamp" in data
