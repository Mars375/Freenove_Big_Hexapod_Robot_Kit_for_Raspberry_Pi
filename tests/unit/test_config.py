"""Unit tests for core.config module."""
import pytest
from pydantic import ValidationError

from core.config import Settings, get_settings


def test_settings_defaults():
    """Test that settings have correct default values."""
    settings = Settings()
    
    assert settings.app_name == "hexapod-robot"
    assert settings.app_version == "2.0.0"
    assert settings.environment in ["development", "staging", "production"]
    assert settings.host == "0.0.0.0"
    assert settings.api_port == 8000


def test_settings_camera_properties():
    """Test camera resolution parsing."""
    settings = Settings(camera_resolution="1920x1080")
    
    assert settings.camera_width == 1920
    assert settings.camera_height == 1080


def test_settings_environment_properties():
    """Test environment helper properties."""
    dev_settings = Settings(environment="development")
    assert dev_settings.is_development is True
    assert dev_settings.is_production is False
    
    prod_settings = Settings(environment="production")
    assert prod_settings.is_production is True
    assert prod_settings.is_development is False


def test_settings_validation():
    """Test that invalid settings raise validation errors."""
    with pytest.raises(ValidationError):
        Settings(max_speed=999)  # Should be <= 10
    
    with pytest.raises(ValidationError):
        Settings(environment="invalid")  # Not a valid choice


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2  # Same instance (cached)


def test_settings_with_custom_values(test_settings):
    """Test creating settings with custom values."""
    assert test_settings.robot_name == "TestBot"
    assert test_settings.api_port == 8888
