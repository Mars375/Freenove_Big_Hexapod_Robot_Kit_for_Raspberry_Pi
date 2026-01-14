"""Hexapod gait patterns - tripod and wave gaits.

This module implements the proven gait algorithms from the original
Freenove hexapod, modernized with clean async code.

Key design: Each call to execute_* runs ONE gait cycle, just like legacy.
The MovementController calls it repeatedly for continuous movement.
"""
import asyncio
import math
import copy
from typing import List, Tuple, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()


class GaitType(Enum):
    """Available gait patterns."""
    TRIPOD = "1"  # Fast, 2 groups of 3 legs alternate
    WAVE = "2"    # Slow, legs move one at a time


@dataclass
class GaitConfig:
    """Gait configuration parameters."""
    step_height: float = 70.0     # Height to lift legs (mm)
    delay: float = 0.005           # Delay between frames (seconds)


class GaitExecutor:
    """Execute hexapod gait patterns.

    This implements the proven algorithm from the original Freenove code.
    Each call to execute() runs ONE complete gait cycle and returns.
    For continuous movement, the caller should loop.
    """

    def __init__(
        self,
        body_points: List[List[float]],
        update_callback: Callable[[List[List[float]]], Awaitable[None]],
        config: GaitConfig = None
    ):
        """Initialize gait executor.

        Args:
            body_points: Initial body-frame foot positions for each leg
                        [[x, y, z], ...] for legs 0-5
            update_callback: Async function to call with new positions
            config: Gait configuration
        """
        self.body_points = copy.deepcopy(body_points)
        self.update_callback = update_callback
        self.config = config or GaitConfig()
        self._running = False

        # Working copy of points - persists across cycles for accumulation
        self._points = copy.deepcopy(body_points)

        # State for continuous movement
        self.x = 0.0
        self.y = 0.0
        self.speed = 5
        self.angle = 0.0
        self.duration = 2.0

        logger.info(
            "gait_executor.initialized",
            step_height=self.config.step_height,
            delay=self.config.delay
        )

    def update_params(self, x: float, y: float, speed: int, angle: float, duration: float = 2.0) -> None:
        """Update movement parameters on the fly."""
        self.x = max(-35, min(35, x))
        self.y = max(-35, min(35, y))
        self.speed = max(2, min(10, speed))
        self.angle = angle
        self.duration = duration
        logger.debug("gait.params_updated", x=self.x, y=self.y, speed=self.speed, angle=self.angle)

    @staticmethod
    def _map_speed_to_frames(speed: int, gait_type: GaitType) -> int:
        """Map speed (2-10) to frame count.

        Exactly matches legacy: map_value(speed, 2, 10, high, low)
        Higher speed = fewer frames = faster movement.
        """
        speed = max(2, min(10, speed))

        if gait_type == GaitType.TRIPOD:
            # Speed 2 -> 126 frames, Speed 10 -> 22 frames
            return round(126 - (speed - 2) * (126 - 22) / 8)
        else:
            # Speed 2 -> 171 frames, Speed 10 -> 45 frames
            return round(171 - (speed - 2) * (171 - 45) / 8)

    def reset_points(self) -> None:
        """Reset working points to initial body points."""
        logger.debug("gait.reset_points.before", points_snapshot=self._points[0])
        self._points = copy.deepcopy(self.body_points)
        logger.debug("gait.reset_points.after", points_snapshot=self._points[0])

    async def execute_tripod_cycle(
        self,
        x: float,
        y: float,
        speed: int,
        angle: float
    ) -> None:
        """Execute ONE tripod gait cycle.

        This matches legacy run_gait exactly - one for loop from 0 to F.

        Args:
            x: Forward movement (-35 to 35)
            y: Lateral movement (-35 to 35)
            speed: Speed 2-10
            angle: Rotation angle (degrees)
        """
        logger.info(
            "gait.tripod_cycle.start",
            x=x, y=y, speed=speed, angle=angle
        )

        F = self._map_speed_to_frames(speed, GaitType.TRIPOD)
        Z = self.config.step_height
        z = Z / F
        delay = self.config.delay

        logger.debug(
            "gait.tripod_cycle.params_calculated",
            frames=F, step_height=Z, z_increment=z, delay=delay
        )

        # Calculate per-leg XY offsets (exactly like legacy)
        angle_rad = math.radians(angle)
        xy = []
        for i in range(6):
            bp = self.body_points[i]
            dx = (
                (bp[0] * math.cos(angle_rad) + bp[1] * math.sin(angle_rad) - bp[0]) + x
            ) / F
            dy = (
                (-bp[0] * math.sin(angle_rad) + bp[1] * math.cos(angle_rad) - bp[1]) + y
            ) / F
            xy.append([dx, dy])

        logger.debug("gait.tripod_cycle.offsets_calculated", xy_offsets=xy[:2])

        # If no movement, just update position
        if x == 0 and y == 0 and angle == 0:
            logger.info("gait.tripod_cycle.no_movement_detected")
            await self.update_callback(self._points)
            return

        logger.info("gait.tripod_cycle.starting_loop", total_frames=F)

        # ONE gait cycle - exactly like legacy
        for j in range(F):
            # ✅ REMOVED: if not self._running: break
            
            if j % 10 == 0:  # Log every 10 frames
                logger.debug("gait.tripod_cycle.frame", frame=j, total=F)

            for i in range(3):
                even = 2 * i      # Legs 0, 2, 4
                odd = 2 * i + 1   # Legs 1, 3, 5

                if j < (F / 8):
                    self._points[even][0] -= 4 * xy[even][0]
                    self._points[even][1] -= 4 * xy[even][1]
                    self._points[odd][0] += 8 * xy[odd][0]
                    self._points[odd][1] += 8 * xy[odd][1]
                    self._points[odd][2] = Z + self.body_points[odd][2]

                elif j < (F / 4):
                    self._points[even][0] -= 4 * xy[even][0]
                    self._points[even][1] -= 4 * xy[even][1]
                    self._points[odd][2] -= z * 8

                elif j < (3 * F / 8):
                    self._points[even][2] += z * 8
                    self._points[odd][0] -= 4 * xy[odd][0]
                    self._points[odd][1] -= 4 * xy[odd][1]

                elif j < (5 * F / 8):
                    self._points[even][0] += 8 * xy[even][0]
                    self._points[even][1] += 8 * xy[even][1]
                    self._points[odd][0] -= 4 * xy[odd][0]
                    self._points[odd][1] -= 4 * xy[odd][1]

                elif j < (3 * F / 4):
                    self._points[even][2] -= z * 8
                    self._points[odd][0] -= 4 * xy[odd][0]
                    self._points[odd][1] -= 4 * xy[odd][1]

                elif j < (7 * F / 8):
                    self._points[even][0] -= 4 * xy[even][0]
                    self._points[even][1] -= 4 * xy[even][1]
                    self._points[odd][2] += z * 8

                else:  # j < F
                    self._points[even][0] -= 4 * xy[even][0]
                    self._points[even][1] -= 4 * xy[even][1]
                    self._points[odd][0] += 8 * xy[odd][0]
                    self._points[odd][1] += 8 * xy[odd][1]

            # Update servos
            try:
                await self.update_callback(self._points)
            except Exception as e:
                logger.error(
                    "gait.tripod_cycle.update_callback_failed",
                    frame=j,
                    error=str(e),
                    exc_info=True
                )
                raise

            await asyncio.sleep(delay)

        logger.info("gait.tripod_cycle.complete", total_frames=F)

    async def execute_wave_cycle(
        self,
        x: float,
        y: float,
        speed: int,
        angle: float
    ) -> None:
        """Execute ONE wave gait cycle.

        Args:
            x: Forward movement (-35 to 35)
            y: Lateral movement (-35 to 35)
            speed: Speed 2-10
            angle: Rotation angle (degrees)
        """
        logger.info(
            "gait.wave_cycle.start",
            x=x, y=y, speed=speed, angle=angle
        )

        F = self._map_speed_to_frames(speed, GaitType.WAVE)
        Z = self.config.step_height
        z = Z / F
        delay = self.config.delay

        logger.debug(
            "gait.wave_cycle.params_calculated",
            frames=F, step_height=Z, z_increment=z, delay=delay
        )

        # Calculate per-leg offsets
        angle_rad = math.radians(angle)
        xy = []
        for i in range(6):
            bp = self.body_points[i]
            dx = (
                (bp[0] * math.cos(angle_rad) + bp[1] * math.sin(angle_rad) - bp[0]) + x
            ) / F
            dy = (
                (-bp[0] * math.sin(angle_rad) + bp[1] * math.cos(angle_rad) - bp[1]) + y
            ) / F
            xy.append([dx, dy])

        logger.debug("gait.wave_cycle.offsets_calculated", xy_offsets=xy[:2])

        if x == 0 and y == 0 and angle == 0:
            logger.info("gait.wave_cycle.no_movement_detected")
            await self.update_callback(self._points)
            return

        # Wave sequence - exactly like legacy
        leg_order = [5, 2, 1, 0, 3, 4]
        logger.info("gait.wave_cycle.starting_loop", leg_order=leg_order, total_frames=F)

        for leg_index, current_leg in enumerate(leg_order):
            # ✅ REMOVED: if not self._running: break

            frames_per_leg = int(F / 6)
            logger.debug(
                "gait.wave_cycle.moving_leg",
                leg=current_leg,
                leg_index=leg_index,
                frames=frames_per_leg
            )

            for j in range(frames_per_leg):
                # ✅ REMOVED: if not self._running: break

                for k in range(6):
                    if k == current_leg:
                        if j < int(frames_per_leg / 3):
                            self._points[k][2] += 18 * z
                        elif j < int(2 * frames_per_leg / 3):
                            self._points[k][0] += 30 * xy[k][0]
                            self._points[k][1] += 30 * xy[k][1]
                        else:
                            self._points[k][2] -= 18 * z
                    else:
                        self._points[k][0] -= 2 * xy[k][0]
                        self._points[k][1] -= 2 * xy[k][1]

                try:
                    await self.update_callback(self._points)
                except Exception as e:
                    logger.error(
                        "gait.wave_cycle.update_callback_failed",
                        leg=current_leg,
                        frame=j,
                        error=str(e),
                        exc_info=True
                    )
                    raise

                await asyncio.sleep(delay)

        logger.info("gait.wave_cycle.complete", total_frames=F)

    async def run_continuous(
        self,
        gait_type: GaitType,
        x: float,
        y: float,
        speed: int,
        angle: float = 0,
        duration: float = 2.0
    ) -> None:
        """Run gait continuously, using dynamic parameters."""
        logger.info(
            f"gait.{gait_type.name.lower()}.continuous_start",
            x=x, y=y, speed=speed, angle=angle, duration=duration
        )

        self._running = True
        self.reset_points()

        # Initial parameters
        self.update_params(x, y, speed, angle, duration)

        start_time = asyncio.get_event_loop().time()
        cycle_count = 0

        while self._running:
            cycle_count += 1
            
            # Check duration - use current self.duration which might have been updated
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= self.duration:
                logger.info(
                    f"gait.{gait_type.name.lower()}.duration_reached",
                    elapsed=elapsed,
                    cycles=cycle_count
                )
                break

            logger.debug(
                f"gait.{gait_type.name.lower()}.continuous_cycle",
                cycle=cycle_count,
                elapsed=elapsed
            )

            # Use current internal parameters for each cycle
            self.reset_points()  # RESET POINTS EVERY CYCLE TO PREVENT DRIFT

            if gait_type == GaitType.TRIPOD:
                await self.execute_tripod_cycle(self.x, self.y, self.speed, self.angle)
            else:
                await self.execute_wave_cycle(self.x, self.y, self.speed, self.angle)

            # If everything is zero, don't hog CPU in busy loop
            if self.x == 0 and self.y == 0 and self.angle == 0:
                logger.debug(f"gait.{gait_type.name.lower()}.continuous_idle")
                await asyncio.sleep(0.1)

        logger.info(
            f"gait.{gait_type.name.lower()}.continuous_complete",
            total_cycles=cycle_count
        )

    def stop(self) -> None:
        """Stop gait execution."""
        self._running = False
        logger.info("gait.stopped")
