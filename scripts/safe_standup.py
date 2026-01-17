#!/usr/bin/env python3
"""Layered stand-up sequence to reduce current spikes."""
import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tachikoma.core.hardware.factory import get_hardware_factory
from tachikoma.core.hardware.movement import MovementController
from tachikoma.core.models.config import load_robot_config


COXA = 0
FEMUR = 1
TIBIA = 2


async def _step_joints(movement: MovementController, joint_type: int, delay: float) -> None:
    for leg_index in range(6):
        await movement.move_single_joint(leg_index, joint_type, 90)
        await asyncio.sleep(delay)


async def main() -> None:
    """Load config, initialize controllers, and stand up safely."""
    config_path = ROOT / "config" / "hardware_map.yaml"
    config = load_robot_config(config_path)

    factory = get_hardware_factory()
    servo = await factory.create_servo_controller()
    movement = MovementController(servo_controller=servo, config=config)

    await _step_joints(movement, COXA, 0.1)
    await _step_joints(movement, TIBIA, 0.1)
    await _step_joints(movement, FEMUR, 0.1)

    await factory.cleanup_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
