"""Pydantic models for hardware configuration."""
from __future__ import annotations

from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field, field_validator


DEFAULT_HARDWARE_MAP_PATH = (
    Path(__file__).resolve().parents[3] / "config" / "hardware_map.yaml"
)


class LegConfig(BaseModel):
    """Per-leg servo configuration."""

    coxa: int = Field(..., ge=0, le=31, description="PWM channel for coxa servo")
    femur: int = Field(..., ge=0, le=31, description="PWM channel for femur servo")
    tibia: int = Field(..., ge=0, le=31, description="PWM channel for tibia servo")
    offsets: List[int] = Field(
        default_factory=lambda: [0, 0, 0],
        description="Per-joint angle offsets (coxa, femur, tibia)",
    )
    is_mirrored: bool = Field(
        default=False, description="True for left-side mirrored legs"
    )

    @field_validator("offsets")
    @classmethod
    def validate_offsets(cls, value: List[int]) -> List[int]:
        if len(value) != 3:
            raise ValueError("offsets must contain 3 values")
        return value


class RobotDimensions(BaseModel):
    """Physical dimensions of a single leg."""

    l1: float = Field(..., gt=0, description="Coxa length (mm)")
    l2: float = Field(..., gt=0, description="Femur length (mm)")
    l3: float = Field(..., gt=0, description="Tibia length (mm)")


class GaitParameters(BaseModel):
    """Parameters that define gait timing and posture."""

    step_height: float = Field(..., gt=0, description="Lift height (mm)")
    body_height: float = Field(..., description="Default body height (mm)")
    step_delay: float = Field(..., gt=0, description="Delay per frame (s)")


class GlobalRobotConfig(BaseModel):
    """Top-level hardware and gait configuration."""

    legs: List[LegConfig] = Field(..., min_length=6, max_length=6)
    dimensions: RobotDimensions
    gait: GaitParameters

    @field_validator("legs")
    @classmethod
    def validate_leg_count(cls, value: List[LegConfig]) -> List[LegConfig]:
        if len(value) != 6:
            raise ValueError("legs must contain 6 entries")
        return value


def load_robot_config(
    path: Path | str = DEFAULT_HARDWARE_MAP_PATH,
) -> GlobalRobotConfig:
    """Load robot configuration from hardware_map.yaml."""
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return GlobalRobotConfig.model_validate(data)
