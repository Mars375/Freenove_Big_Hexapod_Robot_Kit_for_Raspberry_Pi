"""
LED Animation implementations for the robot.
Provides various animation effects for the WS2812B LED strip.
"""
import time
import random
import math
import asyncio
from typing import List, Tuple
import structlog

logger = structlog.get_logger()


class LEDAnimations:
    """LED animation effects for WS2812B strip."""

    def __init__(self, led_strip, num_leds: int = 7):
        """
        Initialize LED animations.
        
        Args:
            led_strip: The underlying LED strip driver (WS2812B)
            num_leds: Number of LEDs in the strip
        """
        self.led_strip = led_strip
        self.num_leds = num_leds
        self._running = False
        self._stop_requested = False

    def stop(self):
        """Request animation to stop."""
        self._stop_requested = True

    async def police(self, duration: float = 5.0, speed: float = 0.1) -> bool:
        """
        Police siren animation - alternating red and blue.
        
        Args:
            duration: Total duration in seconds
            speed: Flash speed in seconds
        """
        logger.info("led_animation.police", duration=duration, speed=speed)
        self._running = True
        self._stop_requested = False
        
        try:
            start_time = time.time()
            red = True
            
            while time.time() - start_time < duration and not self._stop_requested:
                if red:
                    # Red half
                    for i in range(self.num_leds // 2):
                        self.led_strip.set_pixel(i, 255, 0, 0)
                    # Blue half
                    for i in range(self.num_leds // 2, self.num_leds):
                        self.led_strip.set_pixel(i, 0, 0, 255)
                else:
                    # Blue half
                    for i in range(self.num_leds // 2):
                        self.led_strip.set_pixel(i, 0, 0, 255)
                    # Red half
                    for i in range(self.num_leds // 2, self.num_leds):
                        self.led_strip.set_pixel(i, 255, 0, 0)
                
                self.led_strip.show()
                red = not red
                await asyncio.sleep(speed)
            
            self._running = False
            return True
            
        except Exception as e:
            logger.error("led_animation.police_failed", error=str(e))
            self._running = False
            return False

    async def breathing(self, r: int, g: int, b: int, duration: float = 10.0, speed: float = 2.0) -> bool:
        """
        Breathing animation - smooth fade in/out.
        
        Args:
            r, g, b: Base color
            duration: Total duration in seconds
            speed: Breathing cycles per second
        """
        logger.info("led_animation.breathing", color=(r, g, b), duration=duration)
        self._running = True
        self._stop_requested = False
        
        try:
            start_time = time.time()
            steps = 50  # Number of steps in fade
            step_delay = (1.0 / speed) / steps / 2  # Divide by 2 for in and out
            
            while time.time() - start_time < duration and not self._stop_requested:
                # Fade in
                for brightness in range(0, steps + 1):
                    factor = brightness / steps
                    for i in range(self.num_leds):
                        self.led_strip.set_pixel(
                            i,
                            int(r * factor),
                            int(g * factor),
                            int(b * factor)
                        )
                    self.led_strip.show()
                    await asyncio.sleep(step_delay)
                    if self._stop_requested:
                        break
                
                # Fade out
                for brightness in range(steps, -1, -1):
                    factor = brightness / steps
                    for i in range(self.num_leds):
                        self.led_strip.set_pixel(
                            i,
                            int(r * factor),
                            int(g * factor),
                            int(b * factor)
                        )
                    self.led_strip.show()
                    await asyncio.sleep(step_delay)
                    if self._stop_requested:
                        break
            
            self._running = False
            return True
            
        except Exception as e:
            logger.error("led_animation.breathing_failed", error=str(e))
            self._running = False
            return False

    async def fire(self, duration: float = 10.0, intensity: float = 1.0) -> bool:
        """
        Fire animation - flickering red/orange/yellow.
        
        Args:
            duration: Total duration in seconds
            intensity: Fire intensity (0.1 to 1.0)
        """
        logger.info("led_animation.fire", duration=duration, intensity=intensity)
        self._running = True
        self._stop_requested = False
        
        try:
            start_time = time.time()
            
            while time.time() - start_time < duration and not self._stop_requested:
                for i in range(self.num_leds):
                    # Random flicker
                    flicker = random.uniform(0.5, 1.0) * intensity
                    r = int(255 * flicker)
                    g = int(random.uniform(0, 100) * flicker)
                    b = 0
                    
                    self.led_strip.set_pixel(i, r, g, b)
                
                self.led_strip.show()
                await asyncio.sleep(0.05)  # Fast flicker
            
            self._running = False
            return True
            
        except Exception as e:
            logger.error("led_animation.fire_failed", error=str(e))
            self._running = False
            return False

    async def wave(self, r: int, g: int, b: int, duration: float = 10.0, speed: float = 0.5) -> bool:
        """
        Wave animation - color wave propagation.
        
        Args:
            r, g, b: Wave color
            duration: Total duration in seconds
            speed: Wave speed
        """
        logger.info("led_animation.wave", color=(r, g, b), duration=duration)
        self._running = True
        self._stop_requested = False
        
        try:
            start_time = time.time()
            position = 0
            
            while time.time() - start_time < duration and not self._stop_requested:
                for i in range(self.num_leds):
                    # Calculate distance from wave center
                    distance = abs(i - position)
                    # Create wave effect using sine
                    brightness = max(0, 1.0 - (distance / self.num_leds))
                    
                    self.led_strip.set_pixel(
                        i,
                        int(r * brightness),
                        int(g * brightness),
                        int(b * brightness)
                    )
                
                self.led_strip.show()
                position = (position + 1) % (self.num_leds * 2)
                await asyncio.sleep(speed / 10)
            
            self._running = False
            return True
            
        except Exception as e:
            logger.error("led_animation.wave_failed", error=str(e))
            self._running = False
            return False

    async def strobe(self, r: int, g: int, b: int, duration: float = 5.0, speed: float = 0.05) -> bool:
        """
        Strobe animation - rapid on/off flashing.
        
        Args:
            r, g, b: Strobe color
            duration: Total duration in seconds
            speed: Flash speed in seconds
        """
        logger.info("led_animation.strobe", color=(r, g, b), duration=duration)
        self._running = True
        self._stop_requested = False
        
        try:
            start_time = time.time()
            on = True
            
            while time.time() - start_time < duration and not self._stop_requested:
                if on:
                    for i in range(self.num_leds):
                        self.led_strip.set_pixel(i, r, g, b)
                else:
                    for i in range(self.num_leds):
                        self.led_strip.set_pixel(i, 0, 0, 0)
                
                self.led_strip.show()
                on = not on
                await asyncio.sleep(speed)
            
            self._running = False
            return True
            
        except Exception as e:
            logger.error("led_animation.strobe_failed", error=str(e))
            self._running = False
            return False

    async def chase(self, r: int, g: int, b: int, duration: float = 10.0, speed: float = 0.1) -> bool:
        """
        Chase animation - LEDs running in sequence.
        
        Args:
            r, g, b: Chase color
            duration: Total duration in seconds
            speed: Chase speed
        """
        logger.info("led_animation.chase", color=(r, g, b), duration=duration)
        self._running = True
        self._stop_requested = False
        
        try:
            start_time = time.time()
            position = 0
            
            while time.time() - start_time < duration and not self._stop_requested:
                # Clear all LEDs
                for i in range(self.num_leds):
                    self.led_strip.set_pixel(i, 0, 0, 0)
                
                # Light up current position with trail
                self.led_strip.set_pixel(position, r, g, b)
                # Dim trail
                if position > 0:
                    self.led_strip.set_pixel(position - 1, r // 3, g // 3, b // 3)
                
                self.led_strip.show()
                position = (position + 1) % self.num_leds
                await asyncio.sleep(speed)
            
            self._running = False
            return True
            
        except Exception as e:
            logger.error("led_animation.chase_failed", error=str(e))
            self._running = False
            return False
