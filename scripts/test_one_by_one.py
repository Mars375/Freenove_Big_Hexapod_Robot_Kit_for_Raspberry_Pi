#!/usr/bin/env python3
"""Manual servo test, one joint at a time in YAML order."""
import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tachikoma.core.hardware.factory import get_hardware_factory
from tachikoma.core.hardware.movement import MovementController
from tachikoma.core.models.config import load_robot_config


JOINTS = (
    ("Coxa", 0, "coxa"),
    ("Femur", 1, "femur"),
    ("Tibia", 2, "tibia"),
)


async def _wiggle_joint(
    movement: MovementController,
    leg_index: int,
    joint_index: int,
    delta: int = 20,
) -> None:
    angles = [90, 90, 90]
    await movement.set_leg_angles(leg_index, *angles)
    await asyncio.sleep(0.2)
    angles[joint_index] = 90 + delta
    await movement.set_leg_angles(leg_index, *angles)
    await asyncio.sleep(0.3)
    angles[joint_index] = 90
    await movement.set_leg_angles(leg_index, *angles)
    await asyncio.sleep(0.2)


async def main() -> None:
    """Run interactive one-by-one servo test."""
    config_path = ROOT / "config" / "hardware_map.yaml"
    config = load_robot_config(config_path)

    factory = get_hardware_factory()
    servo = await factory.create_servo_controller()
    movement = MovementController(servo_controller=servo, config=config)

    results = []
    try:
        for leg_number, leg in enumerate(config.legs, start=1):
            for joint_name, joint_index, attr in JOINTS:
                channel = getattr(leg, attr)
                print(
                    f"Fait bouger le {joint_name} de la Patte {leg_number} "
                    f"(Channel {channel})..."
                )
                await _wiggle_joint(movement, leg_number - 1, joint_index)
                answer = input("Est-ce que ca bouge ? (y/n/q): ").strip().lower()
                results.append((leg_number, joint_name, channel, answer))
                if answer == "q":
                    raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Arret du test.")
    finally:
        await factory.cleanup_all()

    if results:
        print("Resume:")
        for leg_number, joint_name, channel, answer in results:
            print(
                f"Patte {leg_number} {joint_name} (Channel {channel}): {answer}"
            )


if __name__ == "__main__":
    asyncio.run(main())
