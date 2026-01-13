"""
Pytest configuration and fixtures.
Provides common test fixtures and setup.
"""
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["ENVIRONMENT"] = "development"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """
    Fixture providing a FastAPI TestClient.
    
    Yields:
        Configured test client
    """
    # Set mock hardware to true for testing
    from core.config import settings
    settings.MOCK_HARDWARE = True

    from api.main import app
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_settings():
    """
    Fixture providing test settings.
    
    Returns:
        Settings instance with test configuration
    """
    from core.config import Settings
    
    return Settings(
        environment="development",
        robot_name="TestBot",
        api_port=8888,
    )
