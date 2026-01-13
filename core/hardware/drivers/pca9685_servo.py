"""PCA9685 servo controller implementation"""
from typing import Optional, List, Tuple
import structlog

try:
    from adafruit_servokit import ServoKit
    from adafruit_pca9685 import PCA9685
    from board import SCL, SDA
    import busio
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

from core.hardware.interfaces.servo_controller import IServoController
from core.exceptions import HardwareNotAvailableError

logger = structlog.get_logger()


class PCA9685ServoController(IServoController):
    """Real hardware servo controller using PCA9685 PWM driver
    
    Uses Adafruit CircuitPython libraries for reliable I2C communication.
    Supports 16 channels per PCA9685 chip (extendable to 32 with dual chips).
    
    Hardware Setup:
    - PCA9685 connected via I2C (default address 0x40)
    - Servos connected to channels 0-15 (or 0-31 for dual chip)
    - 5-6V power supply for servos (separate from Pi)
    - Common ground between Pi and servo power
    """
    
    def __init__(
        self,
        channels: int = 16,
        i2c_address: int = 0x40,
        frequency: int = 50,
        min_pulse: int = 500,
        max_pulse: int = 2500
    ):
        """Initialize PCA9685 servo controller
        
        Args:
            channels: Number of servo channels (16 or 32)
            i2c_address: I2C address of PCA9685 (default 0x40)
            frequency: PWM frequency in Hz (default 50 for servos)
            min_pulse: Minimum pulse width in microseconds (default 500)
            max_pulse: Maximum pulse width in microseconds (default 2500)
        """
        if not HARDWARE_AVAILABLE:
            raise HardwareNotAvailableError(
                "PCA9685 libraries not available. Install: "
                "pip install adafruit-circuitpython-servokit adafruit-circuitpython-pca9685"
            )
        
        self._channels = channels
        self._i2c_address = i2c_address
        self._frequency = frequency
        self._min_pulse = min_pulse
        self._max_pulse = max_pulse
        
        self._kit: Optional[ServoKit] = None
        self._pca: Optional[PCA9685] = None
        self._i2c = None
        self._initialized = False
        
        # Track current angles
        self._current_angles: dict[int, int] = {}
        
        logger.info(
            "pca9685_servo.created",
            channels=channels,
            i2c_address=hex(i2c_address),
            frequency=frequency
        )
    
    async def initialize(self) -> None:
        """Initialize PCA9685 hardware via I2C
        
        Raises:
            HardwareNotAvailableError: If I2C or PCA9685 not accessible
        """
        try:
            logger.info("pca9685_servo.initializing")
            
            # Create I2C bus
            self._i2c = busio.I2C(SCL, SDA)
            
            # Initialize PCA9685
            self._pca = PCA9685(self._i2c, address=self._i2c_address)
            self._pca.frequency = self._frequency
            
            # Initialize ServoKit for easy servo control
            self._kit = ServoKit(
                channels=self._channels,
                address=self._i2c_address,
                frequency=self._frequency
            )
            
            # Configure pulse width range for all servos
            for i in range(self._channels):
                self._kit.servo[i].set_pulse_width_range(
                    self._min_pulse,
                    self._max_pulse
                )
            
            self._initialized = True
            
            logger.info(
                "pca9685_servo.initialized",
                channels=self._channels,
                frequency=self._frequency
            )
            
        except Exception as e:
            logger.error(
                "pca9685_servo.init_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise HardwareNotAvailableError(
                f"Failed to initialize PCA9685: {e}"
            ) from e
    
    def is_available(self) -> bool:
        """Check if PCA9685 hardware is initialized and ready"""
        return self._initialized and self._kit is not None
    
    def set_angle(self, channel: int, angle: int) -> None:
        """Set servo angle
        
        Args:
            channel: Servo channel (0 to channels-1)
            angle: Target angle in degrees (0-180)
            
        Raises:
            ValueError: If channel or angle out of range
            RuntimeError: If not initialized
        """
        if not self._initialized or not self._kit:
            raise RuntimeError("PCA9685 not initialized")
        
        if not 0 <= channel < self._channels:
            raise ValueError(
                f"Channel {channel} out of range (0-{self._channels-1})"
            )
        
        if not 0 <= angle <= 180:
            raise ValueError(f"Angle {angle} out of range (0-180)")
        
        try:
            self._kit.servo[channel].angle = angle
            self._current_angles[channel] = angle
            
            logger.debug(
                "pca9685_servo.set_angle",
                channel=channel,
                angle=angle
            )
            
        except Exception as e:
            logger.error(
                "pca9685_servo.set_angle_failed",
                channel=channel,
                angle=angle,
                error=str(e)
            )
            raise
    
    def set_angles(self, angles: List[Tuple[int, int]]) -> None:
        """Set multiple servo angles at once
        
        More efficient than calling set_angle multiple times.
        
        Args:
            angles: List of (channel, angle) tuples
        """
        for channel, angle in angles:
            self.set_angle(channel, angle)
        
        logger.debug(
            "pca9685_servo.set_angles",
            count=len(angles)
        )
    
    def get_angle(self, channel: int) -> Optional[int]:
        """Get last set angle of servo
        
        Note: This returns the last commanded angle, not actual position.
        PCA9685 doesn't have position feedback.
        
        Args:
            channel: Servo channel
            
        Returns:
            Last commanded angle or None if never set
        """
        return self._current_angles.get(channel)
    
    def set_pwm(self, channel: int, pulse_width: int) -> None:
        """Set raw PWM pulse width
        
        Advanced method for fine-grained control.
        
        Args:
            channel: Servo channel
            pulse_width: Pulse width in microseconds (500-2500)
            
        Raises:
            ValueError: If values out of range
            RuntimeError: If not initialized
        """
        if not self._initialized or not self._pca:
            raise RuntimeError("PCA9685 not initialized")
        
        if not 0 <= channel < self._channels:
            raise ValueError(f"Channel {channel} out of range")
        
        if not self._min_pulse <= pulse_width <= self._max_pulse:
            raise ValueError(
                f"Pulse width {pulse_width} out of range "
                f"({self._min_pulse}-{self._max_pulse})"
            )
        
        try:
            # Convert microseconds to 12-bit PWM value
            # PCA9685 runs at specified frequency (default 50Hz = 20ms period)
            period_us = 1_000_000 / self._frequency
            pwm_value = int((pulse_width / period_us) * 4096)
            
            self._pca.channels[channel].duty_cycle = pwm_value
            
            # Estimate angle for tracking
            angle = int((pulse_width - self._min_pulse) / 
                       (self._max_pulse - self._min_pulse) * 180)
            self._current_angles[channel] = angle
            
            logger.debug(
                "pca9685_servo.set_pwm",
                channel=channel,
                pulse_width=pulse_width,
                pwm_value=pwm_value,
                estimated_angle=angle
            )
            
        except Exception as e:
            logger.error(
                "pca9685_servo.set_pwm_failed",
                channel=channel,
                pulse_width=pulse_width,
                error=str(e)
            )
            raise
    
    async def cleanup(self) -> None:
        """Cleanup PCA9685 resources and disable outputs"""
        logger.info("pca9685_servo.cleanup")
        
        try:
            if self._pca:
                # Disable all outputs safely
                self._pca.deinit()
            
            if self._i2c:
                self._i2c.deinit()
            
            self._initialized = False
            self._kit = None
            self._pca = None
            self._i2c = None
            self._current_angles.clear()
            
            logger.info("pca9685_servo.cleanup_complete")
            
        except Exception as e:
            logger.error(
                "pca9685_servo.cleanup_failed",
                error=str(e)
            )
    
    def reset(self) -> None:
        """Reset all servos to neutral position (90 degrees)"""
        logger.info("pca9685_servo.reset")
        
        for channel in range(self._channels):
            try:
                self.set_angle(channel, 90)
            except Exception as e:
                logger.warning(
                    "pca9685_servo.reset_channel_failed",
                    channel=channel,
                    error=str(e)
                )
