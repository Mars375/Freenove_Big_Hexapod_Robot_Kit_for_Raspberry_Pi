#!/usr/bin/env python3
"""
Standalone script for testing the real LEDs on the Raspberry Pi.
"""
import sys
import time
import argparse
import asyncio
import structlog
from pathlib import Path

# Add the project root to the Python path
# This is necessary for the script to be runnable from the 'scripts' directory
# and still find the 'core' module.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.hardware.factory import get_hardware_factory
    from core.hardware.devices.led import LEDStrip
except ImportError as e:
    print(f"Error: Failed to import project modules. Make sure you are running from the correct directory and have all dependencies installed. Details: {e}")
    sys.exit(1)


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()


async def test_colors(led_strip: LEDStrip):
    """Runs a sequence of color tests."""
    log.info("--- Starting Color Test ---")
    colors = {
        "Red": (255, 0, 0),
        "Green": (0, 255, 0),
        "Blue": (0, 0, 255),
        "White": (255, 255, 255),
    }
    for name, (r, g, b) in colors.items():
        log.info(f"Setting color to {name}", color=(r, g, b))
        led_strip.set_color(r, g, b)
        await asyncio.sleep(2)
    log.info("--- Color Test Finished ---")


async def test_brightness(led_strip: LEDStrip):
    """Runs a sequence of brightness tests."""
    log.info("--- Starting Brightness Test ---")

    # Set a base color (White) to see brightness changes
    log.info("Setting base color to White for brightness test")
    led_strip.set_color(255, 255, 255)
    await asyncio.sleep(1)

    levels = {
        "25%": 64,
        "50%": 128,
        "100%": 255,
    }
    for name, level in levels.items():
        log.info(f"Setting brightness to {name}", level=level)
        led_strip.set_brightness(level)
        await asyncio.sleep(2)

    # Restore brightness to 100%
    led_strip.set_brightness(255)
    log.info("--- Brightness Test Finished ---")


async def test_rainbow(led_strip: LEDStrip):
    """Runs the rainbow animation test."""
    log.info("--- Starting Rainbow Animation Test ---")
    log.info("Running rainbow cycle for 2 iterations...")
    led_strip.rainbow_cycle(iterations=2)
    log.info("--- Rainbow Animation Test Finished ---")
    # Note: rainbow_cycle is synchronous in its current implementation,
    # but we call it from an async function for consistency.


async def test_off(led_strip: LEDStrip):
    """Turns the LEDs off."""
    log.info("--- Turning LEDs Off ---")
    led_strip.off()
    await asyncio.sleep(1)
    log.info("--- LEDs are Off ---")


async def main():
    """Main function to run the LED test script."""
    parser = argparse.ArgumentParser(description="Test script for hexapod LEDs.")
    parser.add_argument(
        "--test",
        type=str,
        choices=["colors", "brightness", "rainbow", "off", "all"],
        default="all",
        help="Specify which test to run.",
    )
    args = parser.parse_args()

    log.info("Initializing hardware factory...")
    factory = None
    try:
        factory = get_hardware_factory()
        led_strip = await factory.get_led_strip()

        if not led_strip.is_available():
            log.error("LED hardware is not available. Exiting.")
            # Check for mock mode specifically
            status = led_strip.get_status()
            if status.get("mock_mode", False):
                log.warning("LEDs are running in MOCK_MODE. No real hardware interaction will occur.")
            return

        log.info("LED hardware is available. Starting tests...")

        test_to_run = args.test

        if test_to_run in ["colors", "all"]:
            await test_colors(led_strip)

        if test_to_run in ["brightness", "all"]:
            await test_brightness(led_strip)

        if test_to_run in ["rainbow", "all"]:
            await test_rainbow(led_strip)

        if test_to_run in ["off", "all"]:
            await test_off(led_strip)

        log.info("All tests completed successfully.")

    except Exception as e:
        log.error("An error occurred during the test script.", exc_info=True)

    finally:
        if factory:
            log.info("Cleaning up hardware resources...")
            await factory.cleanup_all()
            log.info("Cleanup complete.")


if __name__ == "__main__":
    asyncio.run(main())
