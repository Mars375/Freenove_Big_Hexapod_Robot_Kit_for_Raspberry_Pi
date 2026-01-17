#!/usr/bin/env python3
"""Interactive servo offset calibration tool."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tachikoma.core.hardware.factory import get_hardware_factory
from tachikoma.core.hardware.movement import MovementController
from tachikoma.core.models.config import GlobalRobotConfig


CONFIG_PATH = ROOT / "config" / "hardware_map.yaml"

JOINT_NAMES = {
    0: "coxa",
    1: "femur",
    2: "tibia",
}


def _prompt_leg() -> Optional[int]:
    while True:
        raw = input("Select leg (1-6) or 'q' to quit: ").strip().lower()
        if raw == "q":
            return None
        if raw.isdigit() and 1 <= int(raw) <= 6:
            return int(raw) - 1
        print("Invalid leg. Enter a value from 1 to 6.")


def _prompt_joint() -> Optional[int]:
    while True:
        raw = input("Select joint (1=coxa, 2=femur, 3=tibia) or 'q' to quit: ").strip().lower()
        if raw == "q":
            return None
        if raw.isdigit() and 1 <= int(raw) <= 3:
            return int(raw) - 1
        print("Invalid joint. Enter 1, 2, or 3.")


def _read_key() -> str:
    try:
        import msvcrt
        return msvcrt.getwch()
    except Exception:
        return input("Enter + / - / s / n / q: ").strip()[:1]


def _save_config(config_data: dict) -> None:
    CONFIG_PATH.write_text(
        yaml.safe_dump(config_data, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def _sync_offsets(config_data: dict, config: GlobalRobotConfig) -> None:
    if "legs" not in config_data or not isinstance(config_data["legs"], list):
        raise ValueError("Invalid config data: missing 'legs' list")

    for leg_index, leg in enumerate(config.legs):
        offsets = list(leg.offsets)
        while len(offsets) < 3:
            offsets.append(0)
        while leg_index >= len(config_data["legs"]):
            config_data["legs"].append({})
        if not isinstance(config_data["legs"][leg_index], dict):
            config_data["legs"][leg_index] = {}
        config_data["legs"][leg_index]["offsets"] = offsets[:3]


def _show_status(config: GlobalRobotConfig, leg_index: int, joint_index: int) -> None:
    leg = config.legs[leg_index]
    joint_name = JOINT_NAMES[joint_index]
    print(
        f"Leg {leg_index + 1} ({'mirrored' if leg.is_mirrored else 'normal'}), "
        f"{joint_name} offset: {leg.offsets[joint_index]:+d} deg"
    )


async def _set_leg_neutral(movement: MovementController, leg_index: int) -> None:
    await movement.set_leg_angles(leg_index, 90, 90, 90)


async def main() -> None:
    if not CONFIG_PATH.exists():
        print(f"Config not found: {CONFIG_PATH}")
        sys.exit(1)

    config_data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(config_data, dict):
        print("Invalid config format.")
        sys.exit(1)
    config = GlobalRobotConfig.model_validate(config_data)

    factory = get_hardware_factory()
    servo = await factory.create_servo_controller()

    movement = MovementController(servo_controller=servo, config=config)

    leg_index = _prompt_leg()
    if leg_index is None:
        return
    joint_index = _prompt_joint()
    if joint_index is None:
        return

    print("Mirrored legs invert angles around 90° after applying offsets.")
    print("Use '+' / '-' to adjust by 1 deg, 's' to save, 'n' new selection, 'q' quit.")
    await _set_leg_neutral(movement, leg_index)
    _show_status(config, leg_index, joint_index)

    while True:
        key = _read_key().lower()

        if key == "+":
            config.legs[leg_index].offsets[joint_index] += 1
            await _set_leg_neutral(movement, leg_index)
            _show_status(config, leg_index, joint_index)
        elif key == "-":
            config.legs[leg_index].offsets[joint_index] -= 1
            await _set_leg_neutral(movement, leg_index)
            _show_status(config, leg_index, joint_index)
        elif key == "s":
            _sync_offsets(config_data, config)
            _save_config(config_data)
            print("Offsets saved.")
        elif key == "n":
            leg_index = _prompt_leg()
            if leg_index is None:
                break
            joint_index = _prompt_joint()
            if joint_index is None:
                break
            await _set_leg_neutral(movement, leg_index)
            _show_status(config, leg_index, joint_index)
        elif key == "q":
            break
        else:
            continue

    await factory.cleanup_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
