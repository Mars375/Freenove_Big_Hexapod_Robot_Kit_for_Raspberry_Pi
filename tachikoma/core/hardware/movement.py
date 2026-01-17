"""Modern hexapod movement controller with HAL.

This module provides the high-level movement controller that:
1. Manages 6 legs with proper coordinate transforms
2. Applies per-joint offsets from configuration
3. Executes gaits via the GaitExecutor
4. Communicates with servos via IServoController
"""
import asyncio
import math
from typing import List, Optional, Any
from dataclasses import dataclass, field
import structlog

try:
    from gpiozero import OutputDevice
except Exception:
    OutputDevice = None


from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
from tachikoma.core.hardware.interfaces import IServoController
from tachikoma.core.hardware.kinematics import HexapodKinematics
from tachikoma.core.hardware.gaits import GaitExecutor, GaitType
from tachikoma.core.hardware.controllers.pid import PIDController
from tachikoma.core.models.config import GlobalRobotConfig, LegConfig, load_robot_config


logger = structlog.get_logger()



# Leg mounting angles (degrees from body X-axis)
# These transform body-frame movements into leg-local coordinates
LEG_ANGLES = [54, 0, -54, -126, 180, 126]


# Leg body offsets for coordinate transform
# These account for the physical offset of each leg from body center
LEG_OFFSETS = [94, 85, 94, 94, 85, 94]


@dataclass
class Leg:
    """Single leg configuration and state."""

    id: int
    servo_pins: List[int]
    mount_angle: float  # Degrees from body X-axis
    offset: float       # Distance offset for transform
    is_left: bool       # True for mirrored legs

    # Current state
    position: List[float] = field(default_factory=lambda: [140.0, 0.0, 0.0])
    angles: List[int] = field(default_factory=lambda: [90, 0, 0])


class MovementController:
    """Modern hexapod movement controller with full gait support.

    Uses dependency injection for servo controller, enabling:
    - Hardware abstraction
    - Easy testing with mocks
    - Multiple servo implementations
    - Clean separation of concerns

    The controller maintains:
    - Body points: foot positions relative to body center
    - Leg positions: foot positions in leg-local frame
    - Joint offsets: per-leg servo offsets from YAML config
    - Current angles: actual servo angles being commanded
    """

    # Default body height below neutral (mm)
    # More negative = lower body (legs extended), less negative = higher body (legs contracted)
    DEFAULT_BODY_HEIGHT = -100.0

    # Initial neutral leg position
    NEUTRAL_POSITION = [140.0, 0.0, 0.0]

    def __init__(
        self,
        servo_controller: Optional[IServoController] = None,
        imu_sensor: Any = None,
        config: Optional[GlobalRobotConfig] = None,
        power_pin: Optional[int] = None,
    ):
        """Initialize movement controller.

        Args:
            servo_controller: Servo controller implementation (injected)
            imu_sensor: IMU sensor for balancing
            config: Robot configuration for servo channels and dimensions
            power_pin: Optional GPIO pin to control servo power
        """
        self._servo = servo_controller
        self._imu = imu_sensor
        self._initialized = False
        self._moving = False
        self._gait_task = None

        # Continuous movement state
        self._movement_params = None  # Tuple: (gait_type, x, y, speed, angle)
        self._movement_loop_task = None  # Background task for infinite movement

        # Balance control
        self._balancing = False
        self._balance_task = None
        self._pid_roll = PIDController(kp=0.5, ki=0.01, kd=0.1)
        self._pid_pitch = PIDController(kp=0.5, ki=0.01, kd=0.1)

        # Robot configuration
        self._config = config or load_robot_config()

        # Body parameters
        self.body_height = self.DEFAULT_BODY_HEIGHT

        # Body points: where feet are relative to body center
        # These define the "standing" position
        self.body_points = [
            [137.1, 189.4, self.body_height],
            [225.0, 0.0, self.body_height],
            [137.1, -189.4, self.body_height],
            [-137.1, -189.4, self.body_height],
            [-225.0, 0.0, self.body_height],
            [-137.1, 189.4, self.body_height],
        ]

        # Leg positions: feet in leg-local frame
        self.leg_positions = [
            [140.0, 0.0, 0.0] for _ in range(6)
        ]

        # Angle cache (per-leg)
        self.current_angles = [[90, 0, 0] for _ in range(6)]

        # Initialize legs
        self.legs = [
            Leg(
                id=i,
                servo_pins=[leg.coxa, leg.femur, leg.tibia],
                mount_angle=LEG_ANGLES[i],
                offset=LEG_OFFSETS[i],
                is_left=leg.is_mirrored,
            )
            for i, leg in enumerate(self._config.legs)
        ]

        # Kinematics engine
        self.kinematics = HexapodKinematics(self._config.dimensions)

        # Gait executor (created on first use)
        self._gait: Optional[GaitExecutor] = None

        # Power control (optional)
        self._power_pin = None
        if power_pin is not None:
            if OutputDevice is None:
                logger.warning("movement.power_pin_unavailable", pin=power_pin)
            else:
                try:
                    self._power_pin = OutputDevice(power_pin)
                    self._power_pin.off()
                except Exception:
                    self._power_pin = None
                    logger.warning("movement.power_pin_failed", pin=power_pin)

        logger.info(
            "movement_controller.created",
            has_servo=servo_controller is not None
        )

    def _transform_angle(self, angle: float, leg_config: LegConfig, joint_index: int) -> int:
        """Apply joint offset, mirroring, and clamp to servo-safe range."""
        if joint_index < 0 or joint_index >= len(leg_config.offsets):
            raise ValueError(f"Invalid joint_index: {joint_index}")

        adjusted = angle + leg_config.offsets[joint_index]
        if leg_config.is_mirrored:
            adjusted = 180 - adjusted

        adjusted = max(0.0, min(180.0, adjusted))
        return int(round(adjusted))

    async def set_leg_angles(self, leg_index: int, coxa: float, femur: float, tibia: float) -> None:
        """Set angles for a single leg after applying offsets and mirroring."""
        if not self._servo:
            raise HardwareNotAvailableError("No servo controller set.")

        if leg_index < 0 or leg_index >= len(self._config.legs):
            raise ValueError(f"Invalid leg_index: {leg_index}")

        leg_config = self._config.legs[leg_index]
        channels = (leg_config.coxa, leg_config.femur, leg_config.tibia)
        raw_angles = (coxa, femur, tibia)

        for joint_index, (channel, angle) in enumerate(zip(channels, raw_angles)):
            transformed = self._transform_angle(angle, leg_config, joint_index)
            await self._servo.set_angle_async(channel, transformed)

    def _transform_coordinates(self, points: List[List[float]]) -> None:
        """Transform body-frame points to leg-local coordinates.

        This applies the rotation for each leg's mounting angle and
        subtracts the leg offset to get positions in the leg's local frame.

        Args:
            points: List of 6 body-frame positions [[x, y, z], ...]
        """
        for i, leg in enumerate(self.legs):
            angle_rad = math.radians(leg.mount_angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Rotate point to leg-local frame
            x_local = points[i][0] * cos_a + points[i][1] * sin_a - leg.offset
            y_local = -points[i][0] * sin_a + points[i][1] * cos_a
            z_local = points[i][2] - 14  # Z offset for leg mounting height

            self.leg_positions[i] = [x_local, y_local, z_local]

    async def _set_leg_angles(self) -> None:
        """Calculate and send servo angles for current leg positions.

        This is the core function that:
        1. Computes IK for each leg position
        2. Applies YAML offsets and mirroring
        3. Sends to servos
        """
        if not self._servo:
            return

        # Check validity first
        if not self.kinematics.check_validity(self.leg_positions):
            logger.warning("movement.invalid_positions")
            return

        # Calculate angles for each leg and send to servos
        for i in range(6):
            pos = self.leg_positions[i]
            # Legacy uses -z, x, y order
            result = self.kinematics.calculate_ik(-pos[2], pos[0], pos[1])
            if not result:
                continue

            self.current_angles[i] = list(result)
            leg_config = self._config.legs[i]
            channels = (leg_config.coxa, leg_config.femur, leg_config.tibia)

            for joint_index, (channel, angle) in enumerate(zip(channels, result)):
                transformed = self._transform_angle(angle, leg_config, joint_index)
                await self._send_servo_angle(channel, transformed)

    async def _send_servo_angle(self, channel: int, angle: int) -> None:
        """Send angle using async API when available."""
        set_angle_async = getattr(self._servo, "set_angle_async", None)
        if set_angle_async is not None:
            await set_angle_async(channel, angle)
        else:
            self._servo.set_angle(channel, angle)

    def set_servo_controller(self, servo_controller: IServoController) -> None:
        """Set servo controller after initialization (for lazy injection)."""
        self._servo = servo_controller
        logger.info("movement_controller.servo_set")

    async def initialize(self) -> None:
        """Initialize servo controller and stand up."""
        if not self._servo:
            raise HardwareNotAvailableError(
                "No servo controller set. Use set_servo_controller() first."
            )

        try:
            logger.info("movement_controller.initializing")

            # Ensure power is ON
            if self._power_pin:
                self._power_pin.off()

            # Initialize servo hardware
            await self._servo.initialize()

            # Stand in neutral position
            await self.stand()

            self._initialized = True
            logger.info("movement_controller.initialized")
            return True
        except Exception as e:
            logger.error("movement_controller.init_failed", error=str(e))
            raise

    @property
    def is_available(self) -> bool:
        """Check if controller is ready to use."""
        return (
            self._initialized and
            self._servo is not None and
            self._servo.is_available()
        )

    async def _update_servos(self, points: List[List[float]]) -> None:
        """Callback for gait executor to update servo positions.

        Args:
            points: New body-frame foot positions
        """
        logger.debug("movement.update_servos.called", points_count=len(points))
        self._transform_coordinates(points)
        await self._set_leg_angles()
        logger.debug("movement.update_servos.complete")

    async def stand(self) -> None:
        """Stand in neutral position."""
        logger.info("movement.stand")

        # Reset to default body points
        self.body_points = [
            [137.1, 189.4, self.body_height],
            [225.0, 0.0, self.body_height],
            [137.1, -189.4, self.body_height],
            [-137.1, -189.4, self.body_height],
            [-225.0, 0.0, self.body_height],
            [-137.1, 189.4, self.body_height],
        ]

        self._transform_coordinates(self.body_points)
        await self._set_leg_angles()
        await asyncio.sleep(0.5)

    async def _movement_loop(self) -> None:
        """Background loop executing gait cycles continuously until stop()."""
        logger.info("movement.continuous_loop.started")

        cycle_count = 0
        
        try:
            while self._moving:
                cycle_count += 1
                logger.debug("movement.loop.iteration_start", cycle=cycle_count)
                
                # Wait for parameters
                if not self._movement_params:
                    logger.debug("movement.loop.waiting_params", cycle=cycle_count)
                    await asyncio.sleep(0.1)
                    continue

                gait_type, x, y, speed, angle = self._movement_params
                
                logger.debug(
                    "movement.loop.params_ready",
                    cycle=cycle_count,
                    params=self._movement_params
                )

                # Safety check: GaitExecutor must exist
                if not self._gait:
                    logger.error("movement.loop.no_gait_executor", cycle=cycle_count)
                    await asyncio.sleep(0.1)
                    continue

                logger.info("movement.loop.before_reset_points", cycle=cycle_count)
                
                # Reset points each cycle to prevent drift
                try:
                    self._gait.reset_points()
                    logger.info("movement.loop.after_reset_points", cycle=cycle_count)
                except Exception as e:
                    logger.error(
                        "movement.loop.reset_points_failed",
                        cycle=cycle_count,
                        error=str(e),
                        exc_info=True
                    )
                    raise

                # Execute ONE gait cycle
                gt = GaitType.TRIPOD if gait_type == "1" else GaitType.WAVE

                logger.info(
                    "movement.loop.executing_cycle",
                    cycle=cycle_count,
                    gait=gt.name,
                    x=x, y=y, speed=speed, angle=angle
                )

                try:
                    logger.info("movement.loop.about_to_call_gait", cycle=cycle_count, gait_type=gt.name)
                    
                    if gt == GaitType.TRIPOD:
                        logger.info("movement.loop.calling_tripod", cycle=cycle_count)
                        result = await self._gait.execute_tripod_cycle(x, y, speed, angle)
                        logger.info("movement.loop.tripod_complete", cycle=cycle_count, result=result)
                    else:
                        logger.info("movement.loop.calling_wave", cycle=cycle_count)
                        result = await self._gait.execute_wave_cycle(x, y, speed, angle)
                        logger.info("movement.loop.wave_complete", cycle=cycle_count, result=result)
                    
                    logger.info("movement.loop.gait_returned", cycle=cycle_count, result=result)
                    
                except Exception as e:
                    logger.error(
                        "movement.loop.gait_execution_failed",
                        cycle=cycle_count,
                        error=str(e),
                        exc_info=True
                    )
                    # Don't raise - let loop continue for now so we can see all errors
                    await asyncio.sleep(0.1)
                    continue

                # Brief pause between cycles
                logger.debug("movement.loop.sleeping", cycle=cycle_count)
                await asyncio.sleep(0.05)

                logger.info("movement.gait_cycle.complete", cycle=cycle_count, gait=gt.name)

        except asyncio.CancelledError:
            logger.info("movement.continuous_loop.cancelled", total_cycles=cycle_count)
            raise
        except Exception as e:
            logger.error(
                "movement.continuous_loop.error",
                cycle=cycle_count,
                error=str(e),
                exc_info=True
            )
            self._moving = False
            raise

    async def move(
        self,
        mode: str = "custom",
        x: int = 0,
        y: int = 25,
        speed: int = 5,
        angle: int = 0,
        gait_type: str = "1"
    ) -> bool:
        """Execute movement command (continuous until stop()).

        If already moving, updates parameters on-the-fly (hot reload).

        Args:
            mode: Predefined mode or "custom"
            x: X axis movement (-35 to 35)
            y: Y axis movement (-35 to 35)
            speed: Movement speed (2 to 10)
            angle: Rotation angle (-10 to 10)
            gait_type: "1" = Tripod, "2" = Wave
        """
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")

        try:
            logger.info(
                "movement.move",
                mode=mode, x=x, y=y, speed=speed, angle=angle, gait_type=gait_type
            )

            # Map mode to parameters
            params = {
                "forward": (0, 25, 0),
                "backward": (0, -25, 0),
                "left": (-25, 0, 0),
                "right": (25, 0, 0),
                "turn_left": (0, 0, 15),
                "turn_right": (0, 0, -15),
                "custom": (x, y, angle),
                "motion": (x, y, angle),  # ✅ FIX: Preserve angle parameter
                "gait": (x, 0, angle),
            }

            x_val, y_val, angle_val = params.get(mode, (x, y, angle))

            # ✅ FIX: Only stop if x, y, AND angle are all zero
            if x_val == 0 and y_val == 0 and angle_val == 0:
                logger.info("movement.move.zero_params.stopping")
                return await self.stop()

            # Update movement parameters
            self._movement_params = (gait_type, x_val, y_val, speed, angle_val)
            logger.info("movement.move.params_set", params=self._movement_params)

            # If already moving, just update params (hot reload)
            if self._moving and self._movement_loop_task and not self._movement_loop_task.done():
                logger.info("movement.params.hot_reload", params=self._movement_params)
                return True

            # Start continuous movement
            logger.info("movement.starting_continuous_loop")
            self._moving = True

            # Create GaitExecutor if needed
            if not self._gait:
                logger.info("movement.creating_gait_executor")
                try:
                    self._gait = GaitExecutor(
                        body_points=self.body_points,
                        update_callback=self._update_servos
                    )
                    logger.info("movement.gait_executor_created", gait_obj=self._gait)
                except Exception as e:
                    logger.error(
                        "movement.gait_executor_creation_failed",
                        error=str(e),
                        exc_info=True
                    )
                    raise

            # Start background loop
            logger.info("movement.launching_loop_task")
            self._movement_loop_task = asyncio.create_task(self._movement_loop())
            logger.info("movement.loop_task_launched", task=self._movement_loop_task)

            return True

        except Exception as e:
            logger.error("movement.move.failed", error=str(e), exc_info=True)
            raise CommandExecutionError(f"Move failed: {e}")

    async def stop(self) -> bool:
        """Stop all movement and return to standing position."""
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")

        try:
            logger.info("movement.stop.initiated")

            # Signal stop
            self._moving = False
            self._movement_params = None

            # Cancel background loop if running
            if self._movement_loop_task and not self._movement_loop_task.done():
                logger.info("movement.stop.cancelling_loop_task")
                self._movement_loop_task.cancel()
                try:
                    await self._movement_loop_task
                except asyncio.CancelledError:
                    logger.debug("movement.stop.loop_task_cancelled")
                    pass

            # Return to standing position
            logger.info("movement.stop.returning_to_stand")
            await self.stand()

            logger.info("movement.stop.complete")
            return True

        except Exception as e:
            logger.error("movement.stop.failed", error=str(e), exc_info=True)
            raise CommandExecutionError(f"Stop failed: {e}")

    async def set_position(self, x: float, y: float, z: float) -> bool:
        """Move body to specified position offset.

        Args:
            x: X offset (-40 to 40)
            y: Y offset (-40 to 40)
            z: Z offset (-20 to 20)
        """
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")

        logger.info("movement.set_position", x=x, y=y, z=z)

        # Clamp values
        x = max(-40, min(40, x))
        y = max(-40, min(40, y))
        z = max(-20, min(20, z))

        # Update body points
        for i in range(6):
            self.body_points[i][0] -= x
            self.body_points[i][1] -= y
            self.body_points[i][2] = -30 - z

        self.body_height = self.body_points[0][2]

        self._transform_coordinates(self.body_points)
        await self._set_leg_angles()

        return True

    async def set_attitude(self, roll: float, pitch: float, yaw: float) -> bool:
        """Set body attitude (rotation).

        Args:
            roll: Roll angle (-15 to 15)
            pitch: Pitch angle (-15 to 15)
            yaw: Yaw angle (-15 to 15)
        """
        if not self.is_available:
            raise HardwareNotAvailableError("Movement controller not initialized")

        logger.info("movement.set_attitude", roll=roll, pitch=pitch, yaw=yaw)

        # Clamp values
        roll = max(-15, min(15, roll))
        pitch = max(-15, min(15, pitch))
        yaw = max(-15, min(15, yaw))

        # Convert to radians
        roll_rad = math.radians(roll)
        pitch_rad = math.radians(pitch)
        yaw_rad = math.radians(yaw)

        # Rotation matrices
        rx = [
            [1, 0, 0],
            [0, math.cos(pitch_rad), -math.sin(pitch_rad)],
            [0, math.sin(pitch_rad), math.cos(pitch_rad)]
        ]
        ry = [
            [math.cos(roll_rad), 0, -math.sin(roll_rad)],
            [0, 1, 0],
            [math.sin(roll_rad), 0, math.cos(roll_rad)]
        ]
        rz = [
            [math.cos(yaw_rad), -math.sin(yaw_rad), 0],
            [math.sin(yaw_rad), math.cos(yaw_rad), 0],
            [0, 0, 1]
        ]

        # Footpoint structure
        footpoints = [
            [137.1, 189.4, 0],
            [225.0, 0.0, 0],
            [137.1, -189.4, 0],
            [-137.1, -189.4, 0],
            [-225.0, 0.0, 0],
            [-137.1, 189.4, 0],
        ]

        # Apply rotation to each footpoint
        position = [0, 0, self.body_height]
        new_points = []

        for fp in footpoints:
            # Combined rotation: R = Rx * Ry * Rz * fp + position
            # Simplified for small angles
            x = position[0] + fp[0] * math.cos(yaw_rad) - fp[1] * math.sin(yaw_rad)
            y = position[1] + fp[0] * math.sin(yaw_rad) + fp[1] * math.cos(yaw_rad)
            z = position[2] + fp[0] * math.sin(pitch_rad) + fp[1] * math.sin(roll_rad)

            new_points.append([x, y, z])

        self._transform_coordinates(new_points)
        await self._set_leg_angles()

        await asyncio.sleep(0.3)
        return True


    async def relax(self) -> None:
        """Disable all servos (relax)."""
        if self._servo:
            await self._servo.relax()
            logger.info("movement.relax")


    async def set_balance_mode(self, enabled: bool) -> None:
        """Toggle IMU-based balance mode."""
        if enabled == self._balancing:
            return

        self._balancing = enabled
        if enabled:
            if self._balance_task:
                self._balance_task.cancel()
            self._balance_task = asyncio.create_task(self._balance_loop())
            logger.info("movement.balance_enabled")
        else:
            if self._balance_task:
                self._balance_task.cancel()
                self._balance_task = None
            logger.info("movement.balance_disabled")
            await self.stand()


    async def _balance_loop(self) -> None:
        """Background loop for active balancing."""
        if not self._imu:
            # Try to get IMU from factory if not provided
            from tachikoma.core.hardware.factory import get_hardware_factory
            factory = get_hardware_factory()
            self._imu = await factory.get_imu()

        self._pid_roll.reset()
        self._pid_pitch.reset()

        try:
            while self._balancing:
                accel = await self._imu.read_accel()
                if accel:
                    # Simple roll/pitch from accel
                    # Match legacy orientation/mapping if needed
                    roll = math.atan2(accel[1], accel[2]) * 180 / math.pi
                    pitch = math.atan2(-accel[0], math.sqrt(accel[1]**2 + accel[2]**2)) * 180 / math.pi

                    # Apply PID
                    adj_roll = self._pid_roll.update(roll)
                    adj_pitch = self._pid_pitch.update(pitch)

                    # Set attitude (internal call without log spam)
                    await self._set_attitude_internal(adj_roll, adj_pitch, 0)

                await asyncio.sleep(0.02) # 50Hz
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("movement.balance_loop_error", error=str(e))
            self._balancing = False


    async def _set_attitude_internal(self, roll: float, pitch: float, yaw: float) -> None:
        """Internal attitude adjustment without extra delays or logs."""
        roll = max(-15, min(15, roll))
        pitch = max(-15, min(15, pitch))
        yaw = max(-15, min(15, yaw))

        roll_rad, pitch_rad, yaw_rad = math.radians(roll), math.radians(pitch), math.radians(yaw)

        footpoints = [
            [137.1, 189.4, 0], [225.0, 0.0, 0], [137.1, -189.4, 0],
            [-137.1, -189.4, 0], [-225.0, 0.0, 0], [-137.1, 189.4, 0],
        ]

        position = [0, 0, self.body_height]
        new_points = []
        for fp in footpoints:
            x = position[0] + fp[0] * math.cos(yaw_rad) - fp[1] * math.sin(yaw_rad)
            y = position[1] + fp[0] * math.sin(yaw_rad) + fp[1] * math.cos(yaw_rad)
            z = position[2] + fp[0] * math.sin(pitch_rad) + fp[1] * math.sin(roll_rad)
            new_points.append([x, y, z])

        self._transform_coordinates(new_points)
        await self._set_leg_angles()


    async def calibrate(self, step: int) -> bool:
        """Handle calibration step."""
        logger.info("movement.calibrate", step=step)
        # Placeholder for future calibration workflow
        return True

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("movement_controller.cleanup")

        # Stop continuous movement
        self._moving = False
        if self._movement_loop_task and not self._movement_loop_task.done():
            self._movement_loop_task.cancel()
            try:
                await self._movement_loop_task
            except asyncio.CancelledError:
                pass

        if self._gait:
            self._gait.stop()

        if self._gait_task and not self._gait_task.done():
            await self._gait_task

        if self._servo:
            try:
                await self.stand()
                await self._servo.cleanup()
            except Exception as e:
                logger.error("movement_controller.cleanup_failed", error=str(e))
