"""
Buzzer controller for passive buzzer (PWM-based tones).
"""
import asyncio
from typing import Optional

# Import RPi.GPIO in a way that is friendly to mocking for tests.
# In a non-Pi environment, this import will fail, and GPIO will be None.
# The class will check for this.
try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    GPIO = None


class BuzzerController:
    """
    Passive buzzer controller using PWM for tones.

    Hardware:
        - GPIO 17 (PWM)
        - Passive buzzer

    Features:
        - Play tones (frequency in Hz)
        - Note playback (C4, D4, etc.)
        - Melodies/sequences
        - Duration control
    """
    NOTES = {
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
        'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
        'C6': 1046.50, 'D6': 1174.66, 'E6': 1318.51,
    }

    def __init__(self, gpio_pin: int = 17):
        """Initialize buzzer controller."""
        if GPIO is None:
            raise RuntimeError("RPi.GPIO library not found. Cannot control hardware.")
        self.gpio_pin = gpio_pin
        self.pwm: Optional[GPIO.PWM] = None
        self._initialized: bool = False

    async def initialize(self) -> None:
        """Initialize GPIO and PWM."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio_pin, 1000)
        self.pwm.start(0)
        self._initialized = True

    async def play_tone(self, frequency: float, duration: float = 0.5, volume: float = 0.5) -> None:
        """Play a tone at specified frequency."""
        if not self._initialized:
            raise RuntimeError("Buzzer not initialized")
        if not 20 <= frequency <= 20000:
            raise ValueError("Frequency must be 20-20000 Hz")
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be 0.0-1.0")

        self.pwm.ChangeFrequency(frequency)
        duty_cycle = volume * 50.0
        self.pwm.ChangeDutyCycle(duty_cycle)
        await asyncio.sleep(duration)
        self.pwm.ChangeDutyCycle(0)

    async def play_note(self, note: str, duration: float = 0.5, volume: float = 0.5) -> None:
        """Play a musical note."""
        if note == 'REST':
            await asyncio.sleep(duration)
            return
        if note not in self.NOTES:
            raise ValueError(f"Unknown note: {note}. Available: {list(self.NOTES.keys())}")
        frequency = self.NOTES[note]
        await self.play_tone(frequency, duration, volume)

    async def play_melody(self, melody: list[tuple[str, float]], volume: float = 0.5) -> None:
        """Play a sequence of notes."""
        for note, duration in melody:
            await self.play_note(note, duration, volume)
            await asyncio.sleep(0.05)

    async def beep(self, count: int = 1, duration: float = 0.1, gap: float = 0.1) -> None:
        """Simple beep(s)."""
        for _ in range(count):
            await self.play_tone(1000, duration, volume=0.5)
            await asyncio.sleep(gap)

    def stop(self) -> None:
        """Stop current sound immediately."""
        if self.pwm:
            self.pwm.ChangeDutyCycle(0)

    async def cleanup(self) -> None:
        """Cleanup GPIO resources."""
        if self.pwm:
            self.pwm.stop()
        GPIO.cleanup(self.gpio_pin)
        self._initialized = False
