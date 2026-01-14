"""Mock servo controller for testing without hardware"""
from typing import Dict, List, Optional
import structlog

from core.hardware.interfaces.servo_controller import IServoController
from core.exceptions import HardwareNotAvailableError

logger = structlog.get_logger()


class MockServoController(IServoController):
    """Mock implementation of servo controller for testing
    
    Records all servo commands for verification in tests.
    Can simulate errors and different hardware states.
    """
    
    def __init__(
        self,
        channels: int = 16,
        simulate_errors: bool = False,
        delay_ms: int = 0
    ):
        """Initialize mock servo controller
        
        Args:
            channels: Number of servo channels to simulate
            simulate_errors: If True, simulate hardware errors
            delay_ms: Simulated delay for servo operations
        """
        self.channels = channels
        self.simulate_errors = simulate_errors
        self.delay_ms = delay_ms
        
        # Track servo states
        self._servo_angles: Dict[int, int] = {}
        self._servo_history: List[tuple] = []  # (channel, angle, timestamp)
        self._initialized = False
        self._running = False
        
        # Error simulation
        self._error_on_channel: Optional[int] = None
        
        logger.info(
            "mock_servo.initialized",
            channels=channels,
            simulate_errors=simulate_errors
        )
    
    async def initialize(self) -> None:
        """Initialize mock servo controller"""
        if self.simulate_errors:
            raise HardwareNotAvailableError("Mock error: initialization failed")
        
        self._initialized = True
        self._running = True
        
        # Initialize all servos to neutral position
        for i in range(self.channels):
            self._servo_angles[i] = 90
        
        logger.info("mock_servo.initialized")
    
    def set_angle(self, channel: int, angle: int) -> None:
        """Set servo angle
        
        Args:
            channel: Servo channel (0-15)
            angle: Angle in degrees (0-180)
        
        Raises:
            ValueError: If channel or angle out of range
            HardwareNotAvailableError: If not initialized or error simulated
        """
        if not self._initialized:
            raise HardwareNotAvailableError("Mock servo not initialized")
        
        if channel < 0 or channel >= self.channels:
            raise ValueError(f"Channel {channel} out of range (0-{self.channels-1})")
        
        if angle < 0 or angle > 180:
            raise ValueError(f"Angle {angle} out of range (0-180)")
        
        if self._error_on_channel == channel:
            raise HardwareNotAvailableError(f"Mock error on channel {channel}")
        
        # Record the command
        import time
        self._servo_angles[channel] = angle
        self._servo_history.append((channel, angle, time.time()))
        
        logger.debug(
            "mock_servo.set_angle",
            channel=channel,
            angle=angle
        )
    
    def get_angle(self, channel: int) -> int:
        """Get current servo angle
        
        Args:
            channel: Servo channel
            
        Returns:
            Current angle in degrees
        """
        if channel not in self._servo_angles:
            return 90  # Default neutral
        return self._servo_angles[channel]
    
    async def set_angles(self, angles: List[tuple]) -> None:
        """Set multiple servo angles at once"""
        for channel, angle in angles:
            self.set_angle(channel, angle)

    def set_pwm(self, channel: int, pulse_width: int) -> None:
        """Set raw PWM pulse width"""
        if not self._initialized:
            raise HardwareNotAvailableError("Mock servo not initialized")
        logger.debug("mock_servo.set_pwm", channel=channel, pulse_width=pulse_width)

    def reset(self) -> None:
        """Reset all servos to neutral position"""
        for i in range(self.channels):
            self.set_angle(i, 90)
        logger.info("mock_servo.reset")

    async def relax(self) -> None:
        """Relax all servos"""
        self._servo_angles.clear()
        logger.info("mock_servo.relax")

    async def cleanup(self) -> None:
        """Cleanup mock resources"""
        await self.relax()
        self._running = False
        self._initialized = False
        logger.info(
            "mock_servo.cleanup",
            commands_executed=len(self._servo_history)
        )
    
    def is_available(self) -> bool:
        return self._initialized

    # Testing utilities
    
    def get_command_history(self) -> List[tuple]:
        """Get history of all servo commands
        
        Returns:
            List of (channel, angle, timestamp) tuples
        """
        return self._servo_history.copy()
    
    def get_command_count(self, channel: Optional[int] = None) -> int:
        """Get number of commands sent
        
        Args:
            channel: If specified, count only for this channel
            
        Returns:
            Number of commands
        """
        if channel is None:
            return len(self._servo_history)
        return sum(1 for c, _, _ in self._servo_history if c == channel)
    
    def clear_history(self) -> None:
        """Clear command history"""
        self._servo_history.clear()
    
    def simulate_error_on_channel(self, channel: int) -> None:
        """Simulate hardware error on specific channel
        
        Args:
            channel: Channel to simulate error on
        """
        self._error_on_channel = channel
    
    def clear_error_simulation(self) -> None:
        """Clear error simulation"""
        self._error_on_channel = None
    
    @property
    def is_initialized(self) -> bool:
        """Check if controller is initialized"""
        return self._initialized
    
    @property
    def is_running(self) -> bool:
        """Check if controller is running"""
        return self._running
