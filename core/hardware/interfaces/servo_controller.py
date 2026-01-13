"""Servo controller interface for hardware abstraction"""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import structlog

logger = structlog.get_logger()


class IServoController(ABC):
    """Abstract interface for servo control hardware
    
    This interface abstracts the servo hardware implementation,
    allowing for multiple backends (PCA9685, mock, simulator, etc.)
    and making the code testable without physical hardware.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize servo hardware
        
        Raises:
            HardwareError: If hardware initialization fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if servo hardware is available and initialized
        
        Returns:
            bool: True if hardware is ready, False otherwise
        """
        pass
    
    @abstractmethod
    def set_angle(self, channel: int, angle: int) -> None:
        """Set servo angle on specific channel
        
        Args:
            channel: Servo channel (0-31 for PCA9685)
            angle: Target angle in degrees (0-180)
            
        Raises:
            ValueError: If channel or angle out of range
            HardwareError: If command fails
        """
        pass
    
    @abstractmethod
    def set_angles(self, angles: List[Tuple[int, int]]) -> None:
        """Set multiple servo angles at once (batch operation)
        
        Args:
            angles: List of (channel, angle) tuples
            
        Raises:
            ValueError: If any channel or angle out of range
            HardwareError: If command fails
        """
        pass
    
    @abstractmethod
    def get_angle(self, channel: int) -> Optional[int]:
        """Get current angle of servo
        
        Args:
            channel: Servo channel
            
        Returns:
            Current angle in degrees, or None if unknown
        """
        pass
    
    @abstractmethod
    def set_pwm(self, channel: int, pulse_width: int) -> None:
        """Set raw PWM pulse width (advanced)
        
        Args:
            channel: Servo channel
            pulse_width: Pulse width in microseconds (typically 500-2500)
            
        Raises:
            ValueError: If values out of range
            HardwareError: If command fails
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup and release hardware resources
        
        Should be called before shutdown to safely disable servos
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset all servos to neutral position (90 degrees)"""
        pass
