#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone test script for LED hardware on the Freenove Hexapod Robot.
"""

import argparse
import sys
import time
import structlog

# Set up structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()

# Attempt to import the hardware factory. This will only work on the Raspberry Pi.
try:
    from core.hardware.factory import get_hardware_factory
except ImportError:
    log.error(
        "Hardware factory not found. This script must be run on the robot.",
        hint="Ensure 'core' is in your PYTHONPATH."
    )
    sys.exit(1)


def main():
    """Main function to run the LED tests."""
    parser = argparse.ArgumentParser(description="Real-world LED Test Script")
    parser.add_argument('--colors', action='store_true', help='Run only the color test.')
    parser.add_argument('--brightness', action='store_true', help='Run only the brightness test.')
    parser.add_argument('--rainbow', action='store_true', help='Run only the rainbow animation test.')
    parser.add_argument('--off', action='store_true', help='Run only the off test.')
    args = parser.parse_args()

    log.info("Starting LED hardware test...")

    factory = get_hardware_factory()
    led = factory.get_led()

    if not led.is_available():
        log.error("LED hardware is not available. Exiting.")
        sys.exit(1)

    log.info("LED hardware is available.")

    # Determine which tests to run
    run_all = not any([args.colors, args.brightness, args.rainbow, args.off])

    try:
        if run_all or args.colors:
            test_colors(led)
        if run_all or args.brightness:
            test_brightness(led)
        if run_all or args.rainbow:
            test_rainbow(led)
        if run_all or args.off:
            test_off(led)

    except KeyboardInterrupt:
        log.warning("Test interrupted by user.")
    except Exception as e:
        log.error("An error occurred during testing.", exc_info=e)
    finally:
        log.info("Cleaning up...")
        led.off()


def test_colors(led):
    """Test basic colors."""
    log.info("--- Testing Basic Colors ---")
    colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "white": (255, 255, 255)}
    for name, rgb in colors.items():
        log.info(f"Setting color to {name}", color=rgb)
        led.set_color(rgb)
        time.sleep(2)


def test_brightness(led):
    """Test brightness levels."""
    log.info("--- Testing Brightness ---")
    led.set_color((255, 255, 255)) # White for brightness test
    levels = [0, 50, 100]
    for level in levels:
        log.info(f"Setting brightness to {level}%")
        led.set_brightness(level)
        time.sleep(2)


def test_rainbow(led):
    """Test rainbow animation."""
    log.info("--- Testing Rainbow Animation ---")
    log.info("Running rainbow animation for 2 cycles (10 seconds)")
    led.rainbow(cycles=2)
    time.sleep(10)


def test_off(led):
    """Test turning the LEDs off."""
    log.info("--- Testing LED Off ---")
    led.off()
    time.sleep(1)



if __name__ == "__main__":
    main()
