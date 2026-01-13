"""Ultrasonic sensor driver via ADC.

Measures distance using ADS7830 ADC channel.
"""
from typing import Optional

try:
    from .adc import ADCController
    ADC_AVAILABLE = True
except ImportError:
    ADC_AVAILABLE = False


class UltrasonicSensor:
    """Ultrasonic distance sensor via ADC."""
    
    CHANNEL = 0  # ADC channel for ultrasonic sensor
    
    def __init__(self, adc: Optional['ADCController'] = None, channel: int = CHANNEL):
        """Initialize ultrasonic sensor.
        
        Args:
            adc: ADC controller instance
            channel: ADC channel (default 0)
        """
        self.channel = channel
        
        if adc:
            self.adc = adc
        elif ADC_AVAILABLE:
            self.adc = ADCController()
        else:
            self.adc = None
            print("ADC not available, using mock ultrasonic")
    
    def read_raw(self) -> int:
        """Read raw ADC value.
        
        Returns:
            ADC value 0-255
        """
        if self.adc:
            return self.adc.read_channel(self.channel)
        return 0
    
    def read_distance(self) -> float:
        """Read distance in cm.
        
        Returns:
            Distance in centimeters
        """
        raw = self.read_raw()
        # Conversion: ~5V ADC range, sensor outputs proportional voltage
        # This is a simplified conversion, adjust based on sensor specs
        distance_cm = (raw / 255.0) * 500  # Max ~500cm range
        return distance_cm
    
    def is_obstacle(self, threshold_cm: float = 30.0) -> bool:
        """Check if obstacle detected within threshold.
        
        Args:
            threshold_cm: Detection threshold in cm
            
        Returns:
            True if obstacle detected
        """
        return self.read_distance() < threshold_cm
