"""Buzzer driver for Freenove Hexapod.

Based on Freenove buzzer.py - GPIO 17 control.
"""
try:
    from gpiozero import OutputDevice
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


class BuzzerController:
    """Simple buzzer controller for GPIO 17."""
    
    PIN = 17
    
    def __init__(self, pin: int = PIN):
        """Initialize buzzer.
        
        Args:
            pin: GPIO pin number (default 17)
        """
        self.pin = pin
        
        if GPIOZERO_AVAILABLE:
            self.buzzer = OutputDevice(self.pin)
        else:
            self.buzzer = None
            print("gpiozero not available, using mock buzzer")
    
    def on(self):
        """Turn buzzer on."""
        if self.buzzer:
            self.buzzer.on()
    
    def off(self):
        """Turn buzzer off."""
        if self.buzzer:
            self.buzzer.off()
    
    def beep(self, duration: float = 0.1):
        """Beep for specified duration.
        
        Args:
            duration: Beep duration in seconds
        """
        self.on()
        import time
        time.sleep(duration)
        self.off()
    
    def close(self):
        """Cleanup GPIO resources."""
        self.off()
        if self.buzzer:
            self.buzzer.close()
