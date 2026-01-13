"""Sensor reader interface for hardware abstraction"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ISensorReader(ABC):
    """Interface for sensor reading operations
    
    Provides common interface for all sensor types (IMU, ultrasonic, ADC, etc.)
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize sensor hardware
        
        Raises:
            HardwareNotAvailableError: If sensor hardware not available
        """
        pass
    
    @abstractmethod
    async def read(self) -> Dict[str, Any]:
        """Read sensor data
        
        Returns:
            Dictionary with sensor readings
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup sensor resources"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if sensor is available and ready
        
        Returns:
            True if sensor is operational
        """
        pass
    
    @property
    @abstractmethod
    def sensor_type(self) -> str:
        """Get sensor type identifier
        
        Returns:
            Sensor type string (e.g., 'imu', 'ultrasonic', 'adc')
        """
        pass


class IIMUSensor(ISensorReader):
    """Interface for IMU (Inertial Measurement Unit) sensors"""
    
    @abstractmethod
    async def read_acceleration(self) -> Dict[str, float]:
        """Read acceleration data
        
        Returns:
            Dict with 'x', 'y', 'z' acceleration values in m/s²
        """
        pass
    
    @abstractmethod
    async def read_gyro(self) -> Dict[str, float]:
        """Read gyroscope data
        
        Returns:
            Dict with 'x', 'y', 'z' angular velocity in rad/s
        """
        pass
    
    @abstractmethod
    async def read_temperature(self) -> float:
        """Read temperature from IMU
        
        Returns:
            Temperature in Celsius
        """
        pass


class IDistanceSensor(ISensorReader):
    """Interface for distance sensors (ultrasonic, IR, etc.)"""
    
    @abstractmethod
    async def read_distance(self) -> float:
        """Read distance measurement
        
        Returns:
            Distance in centimeters
        """
        pass
    
    @property
    @abstractmethod
    def max_range(self) -> float:
        """Maximum detection range in cm"""
        pass
    
    @property
    @abstractmethod
    def min_range(self) -> float:
        """Minimum detection range in cm"""
        pass


class IADCSensor(ISensorReader):
    """Interface for ADC (Analog-to-Digital Converter) sensors"""
    
    @abstractmethod
    async def read_voltage(self, channel: int) -> float:
        """Read voltage from specific channel
        
        Args:
            channel: ADC channel number
            
        Returns:
            Voltage value in volts
        """
        pass
    
    @abstractmethod
    async def read_all_channels(self) -> Dict[int, float]:
        """Read all ADC channels
        
        Returns:
            Dict mapping channel number to voltage
        """
        pass
    
    @property
    @abstractmethod
    def num_channels(self) -> int:
        """Number of available ADC channels"""
        pass
