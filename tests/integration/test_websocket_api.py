"""Integration tests for WebSocket endpoints."""
from fastapi.testclient import TestClient


def test_websocket_test_page(test_client: TestClient):
    """Test WebSocket test page is accessible."""
    response = test_client.get("/api/v1/ws/test")
    
    assert response.status_code == 200
    assert "WebSocket" in response.text
