"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables and config files.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and config files."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = Field(default="hexapod-robot", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server bind address")
    api_port: int = Field(default=8000, description="API server port")
    video_port: int = Field(default=8002, description="Video stream port")
    command_port: int = Field(default=5002, description="Command TCP port")
    
    # Security
    api_key: str = Field(default="dev-key-change-in-production", description="API key")
    jwt_secret: str = Field(default="dev-secret-change-in-production", description="JWT secret")
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )
    
    # Robot Configuration
    robot_name: str = Field(default="Hexapod-01", description="Robot identifier")
    max_speed: int = Field(default=10, ge=1, le=10, description="Maximum movement speed")
    max_step_length: int = Field(default=35, ge=1, le=50, description="Maximum step length")
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_file: Path = Field(default=Path("logs/robot.log"), description="Log file path")
    
    # Redis (optional)
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    
    # Orion Integration
    orion_brain_url: str = Field(
        default="http://localhost:9000", description="Orion Brain API URL"
    )
    orion_guardian_enabled: bool = Field(
        default=True, description="Enable Orion Guardian integration"
    )
    orion_healer_enabled: bool = Field(
        default=True, description="Enable Orion Healer integration"
    )
    
    # Camera
    camera_enabled: bool = Field(default=True, description="Enable camera")
    camera_fps: int = Field(default=30, ge=1, le=60, description="Camera FPS")
    camera_resolution: str = Field(default="640x480", description="Camera resolution")
    
    # Sensors
    imu_enabled: bool = Field(default=True, description="Enable IMU sensor")
    ultrasonic_enabled: bool = Field(default=True, description="Enable ultrasonic sensor")
    
    @property
    def camera_width(self) -> int:
        """Extract camera width from resolution string."""
        return int(self.camera_resolution.split("x")[0])
    
    @property
    def camera_height(self) -> int:
        """Extract camera height from resolution string."""
        return int(self.camera_resolution.split("x")[1])
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience access
settings = get_settings()
