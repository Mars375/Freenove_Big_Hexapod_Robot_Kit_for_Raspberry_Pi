#!/usr/bin/env python3
"""Inverse kinematics test with a breathing body motion."""
import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tachikoma.core.hardware.factory import get_hardware_factory
from tachikoma.core.hardware.kinematics import HexapodKinematics
from tachikoma.core.hardware.movement import MovementController
from tachikoma.core.models.config import load_robot_config


NEUTRAL_X = 140.0
NEUTRAL_Y = 0.0


async def main() -> None:
    """Run a full down/up breathing cycle."""
    config_path = ROOT / "config" / "hardware_map.yaml"
    config = load_robot_config(config_path)
    kinematics = HexapodKinematics(config.dimensions)

    factory = get_hardware_factory()
    servo = await factory.create_servo_controller()
    movement = MovementController(servo_controller=servo, config=config)

    z_values = list(range(-25, -61, -1)) + list(range(-59, -24, 1))
    for z_body in z_values:
        z_down = -float(z_body)
        for leg_index in range(len(config.legs)):
            angles = kinematics.calculate_ik(NEUTRAL_X, NEUTRAL_Y, z_down)
            if angles is None:
                continue
            movement.set_leg_angles(leg_index, *angles)
        await asyncio.sleep(0.02)

    await factory.cleanup_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
