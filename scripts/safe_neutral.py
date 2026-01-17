#!/usr/bin/env python3
"""Move all servos to neutral position leg-by-leg for safety."""
import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tachikoma.core.hardware.factory import get_hardware_factory
from tachikoma.core.hardware.movement import MovementController
from tachikoma.core.models.config import load_robot_config


async def main() -> None:
    """Load config, initialize controllers, and set neutral pose safely."""
    config_path = ROOT / "config" / "hardware_map.yaml"
    config = load_robot_config(config_path)

    factory = get_hardware_factory()
    servo = await factory.create_servo_controller()

    movement = MovementController(servo_controller=servo, config=config)

    for leg_index in range(len(config.legs)):
        movement.set_leg_angles(leg_index, 90, 90, 90)
        await asyncio.sleep(0.1)

    await factory.cleanup_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
