"""Core Pydantic models for configuration."""

from .config import (
    GaitParameters,
    GlobalRobotConfig,
    LegConfig,
    RobotDimensions,
    load_robot_config,
)

__all__ = [
    "GaitParameters",
    "GlobalRobotConfig",
    "LegConfig",
    "RobotDimensions",
    "load_robot_config",
]
