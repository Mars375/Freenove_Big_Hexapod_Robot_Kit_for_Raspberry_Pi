"""
Core types for the Tachikoma project.

This file contains shared enumerations, data structures, and type definitions
used across the core architecture of the robot. It is intended to be a
dependency-free module that can be safely imported by any other component
without causing circular dependencies.

- Enums: Define strict, named constants for robot states and modes.
- RobotState: A dataclass representing the single source of truth for the
  robot's current state.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# --- Shared Enumerations ---

class GaitType(Enum):
    """Defines the available walking gaits for the hexapod."""
    TRIPOD = "tripod"
    WAVE = "wave"
    RIPPLE = "ripple"


class LedMode(Enum):
    """Defines the operating modes for the LED controller."""
    OFF = "off"
    SOLID = "solid"
    RAINBOW = "rainbow"


class RobotMode(Enum):
    """Defines the high-level operating modes of the robot."""
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"
    SLEEP = "sleep"


# --- Robot State ---

@dataclass
class SensorState:
    """
    Represents a snapshot of all sensor readings at a specific time.
    """
    timestamp: float
    obstacle_distance_cm: Optional[float]
    imu_ok: bool


@dataclass
class RobotState:
    """
    Represents the single source of truth for the robot's current state.

    This structure holds telemetry data and status information, but does not
    contain any configuration or command parameters. It is a snapshot of
    "what the robot is now".
    """
    timestamp: float

    # Energy Management
    battery_voltage: float
    battery_percent: float

    # Movement Dynamics
    velocity_x: float
    velocity_y: float
    rotation: float
    speed: int
    gait: GaitType

    # Body Posture
    body_z: float
    pitch: float
    roll: float
    yaw: float

    # Sensor Readings
    obstacle_distance_cm: Optional[float]
    imu_ok: bool
    sensors_ok: bool

    # System Status
    mode: RobotMode
    errors: list[str]
