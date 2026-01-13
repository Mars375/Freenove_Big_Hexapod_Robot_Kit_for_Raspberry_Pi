"""
Pydantic models for API request and response validation.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MovementMode(str, Enum):
    """Movement mode enumeration."""
    MOTION = "motion"
    GAIT = "gait"


class LEDMode(str, Enum):
    """LED mode enumeration."""
    OFF = "off"
    SOLID = "solid"
    CHASE = "chase"
    BLINK = "blink"
    BREATHING = "breathing"
    RAINBOW = "rainbow"


# ============= Movement Models =============

class MoveRequest(BaseModel):
    """Request model for robot movement."""
    mode: MovementMode = Field(default=MovementMode.MOTION, description="Movement mode")
    x: int = Field(ge=-35, le=35, default=0, description="X axis step length")
    y: int = Field(ge=-35, le=35, default=0, description="Y axis step length")
    speed: int = Field(ge=2, le=10, default=5, description="Movement speed")
    angle: int = Field(ge=-10, le=10, default=0, description="Rotation angle")

    @field_validator('mode', mode='before')
    @classmethod
    def validate_mode(cls, v):
        """Convert string mode to enum."""
        if isinstance(v, str):
            if v in ["1", "motion"]:
                return MovementMode.MOTION
            elif v in ["2", "gait"]:
                return MovementMode.GAIT
        return v


class MoveCommand(BaseModel):
    """Command model for robot movement."""
    mode: str = Field(default="motion", description="Movement mode")
    x: int = Field(ge=-35, le=35, default=0, description="X axis step length")
    y: int = Field(ge=-35, le=35, default=0, description="Y axis step length")
    speed: int = Field(ge=2, le=10, default=5, description="Movement speed")
    angle: int = Field(ge=-10, le=10, default=0, description="Rotation angle")


class AttitudeRequest(BaseModel):
    """Request model for robot attitude control."""
    roll: int = Field(ge=-15, le=15, default=0, description="Roll angle")
    pitch: int = Field(ge=-15, le=15, default=0, description="Pitch angle")
    yaw: int = Field(ge=-15, le=15, default=0, description="Yaw angle")


class AttitudeCommand(BaseModel):
    """Command model for robot attitude control."""
    roll: float = Field(ge=-15, le=15, default=0, description="Roll angle")
    pitch: float = Field(ge=-15, le=15, default=0, description="Pitch angle")
    yaw: float = Field(ge=-15, le=15, default=0, description="Yaw angle")


class PositionRequest(BaseModel):
    """Request model for robot position control."""
    x: int = Field(ge=-40, le=40, default=0, description="X position")
    y: int = Field(ge=-40, le=40, default=0, description="Y position")
    z: int = Field(ge=-20, le=20, default=0, description="Z position")


class MovementResponse(BaseModel):
    """Response model for movement commands."""
    success: bool
    message: str
    command: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============= Camera Models =============

class CameraRotateRequest(BaseModel):
    """Request model for camera rotation."""
    horizontal: int = Field(ge=-90, le=90, default=0, description="Horizontal angle")
    vertical: int = Field(ge=-90, le=90, default=0, description="Vertical angle")


class CameraConfigResponse(BaseModel):
    """Response model for camera configuration."""
    enabled: bool
    fps: int
    resolution: str
    horizontal_angle: int
    vertical_angle: int


# ============= Sensor Models =============

class IMUData(BaseModel):
    """IMU sensor data."""
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    temperature: Optional[float] = None


class UltrasonicData(BaseModel):
    """Ultrasonic sensor data."""
    distance: float = Field(description="Distance in centimeters")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BatteryData(BaseModel):
    """Battery sensor data."""
    voltage: float = Field(description="Voltage in volts")
    percentage: int = Field(ge=0, le=100, description="Battery percentage")
    is_charging: bool = False
    is_low: bool = False
    is_critical: bool = False


class AllSensorsData(BaseModel):
    """All sensors data combined."""
    imu: Optional[IMUData] = None
    ultrasonic: Optional[UltrasonicData] = None
    battery: Optional[BatteryData] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============= LED Models =============

class LEDColorRequest(BaseModel):
    """Request model for LED color."""
    red: int = Field(ge=0, le=255, default=0, description="Red value")
    green: int = Field(ge=0, le=255, default=0, description="Green value")
    blue: int = Field(ge=0, le=255, default=0, description="Blue value")


class LEDModeRequest(BaseModel):
    """Request model for LED mode."""
    mode: LEDMode
    color: Optional[LEDColorRequest] = None


class LEDResponse(BaseModel):
    """Response model for LED commands."""
    success: bool
    mode: str
    message: str


# ============= Buzzer Models =============

class BuzzerCommand(BaseModel):
    """Command to control buzzer"""
    frequency: int = Field(..., ge=100, le=5000, description="Buzzer frequency in Hz")
    duration: float = Field(..., ge=0.1, le=5.0, description="Buzzer duration in seconds")
    enabled: bool = Field(default=True, description="Enable buzzer beep")


# ============= System Models =============

class SystemStatus(BaseModel):
    """System status response."""
    robot_name: str
    version: str
    uptime_seconds: float
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    temperature: Optional[float] = None


class CommandResponse(BaseModel):
    """Generic command response."""
    success: bool
    message: str
    data: Optional[dict] = None
    command: Optional[str] = None
    mode: Optional[str] = None
    timestamp: Optional[str] = None


# ============= Aliases for Compatibility =============
StandardResponse = CommandResponse  # Alias for backward compatibility
