#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified command-line interface for hardware testing of the Hexapod robot.

This script provides a centralized way to test various hardware components
of the robot, such as LEDs, servos, IMU, ADC, and buzzer. It uses
the project's Hardware Abstraction Layer (HAL) to interact with the
hardware components.

The script is designed to be run from the command line and offers various
options to test specific components or all of them. It also includes an
interactive mode if no arguments are provided.

Usage examples:
  - Test all components:
    python scripts/test_hardware.py --all

  - Test only the LEDs:
    python scripts/test_hardware.py --led

  - Test servos and IMU:
    python scripts/test_hardware.py --servo --imu

  - Run in interactive mode:
    python scripts/test_hardware.py
"""

import sys
import argparse
import asyncio
import structlog
from pathlib import Path
from typing import Dict, Any, Coroutine

# Add the project root to the Python path to allow module imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.hardware.factory import HardwareFactory, get_hardware_factory
    from core.hardware.devices.led import LEDStrip
    from core.hardware.drivers.servo import Servo
    from core.hardware.drivers.imu import IMU
    from core.hardware.drivers.adc import ADC
    from core.hardware.devices.buzzer import Buzzer
except ImportError as e:
    print(f"Error: Failed to import project modules. Details: {e}")
    sys.exit(1)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()


class HardwareTester:
    """
    A class to encapsulate hardware testing logic.

    This class uses the HardwareFactory to get instances of hardware
    components and provides methods to test each of them.
    """

    def __init__(self, factory: HardwareFactory):
        self.factory = factory
        self.log = log.bind(tester=self.__class__.__name__)

    async def test_leds(self) -> bool:
        """
        Tests the LED strip with a sequence of colors, brightness levels,
        and animations.
        """
        self.log.info("--- Starting LED Test ---")
        led_strip = await self.factory.get_led_strip()

        if not led_strip or not led_strip.is_available():
            self.log.error("LED hardware is not available or failed to initialize.")
            return False

        try:
            self.log.info("Testing colors...")
            colors = {"Red": (255, 0, 0), "Green": (0, 255, 0), "Blue": (0, 0, 255)}
            for name, color in colors.items():
                self.log.info(f"Setting color to {name}")
                led_strip.set_color(*color)
                await asyncio.sleep(1)

            self.log.info("Testing brightness...")
            led_strip.set_color(255, 255, 255)  # White for brightness test
            for level in [32, 128, 255]:
                self.log.info(f"Setting brightness to {level}")
                led_strip.set_brightness(level)
                await asyncio.sleep(1)

            self.log.info("Testing rainbow animation...")
            led_strip.rainbow_cycle(iterations=1)
            await asyncio.sleep(0.5)

            self.log.info("Turning LEDs off.")
            led_strip.off()
            self.log.info("--- LED Test Successful ---")
            return True
        except Exception as e:
            self.log.error("An error occurred during LED test.", exc_info=True)
            return False

    async def test_servos(self) -> bool:
        """
        Tests the servo controller (PCA9685) and attached servos.
        """
        self.log.info("--- Starting Servo Test ---")
        servo_controller = await self.factory.get_servo_controller()

        if not servo_controller or not servo_controller.is_available():
            self.log.error("Servo controller (PCA9685) is not available.")
            return False

        try:
            self.log.info("Testing servo controller PWM setting.")
            # Simple test to set a PWM value on a channel
            await servo_controller.set_pwm(0, 0, 2048)  # 50% duty cycle on channel 0
            await asyncio.sleep(1)
            await servo_controller.set_pwm(0, 0, 0) # Turn off
            self.log.info("Servo controller test successful.")

            # Placeholder for individual servo tests if needed

            self.log.info("--- Servo Test Successful ---")
            return True
        except Exception as e:
            self.log.error("An error occurred during servo test.", exc_info=True)
            return False

    async def test_imu(self) -> bool:
        """
        Tests the IMU (MPU6050) by reading sensor data.
        """
        self.log.info("--- Starting IMU Test ---")
        imu = await self.factory.get_imu()

        if not imu or not imu.is_available():
            self.log.error("IMU (MPU6050) is not available.")
            return False

        try:
            self.log.info("Reading IMU data...")
            accel = await imu.read_accel()
            gyro = await imu.read_gyro()
            temp = await imu.read_temperature()

            if accel:
                self.log.info(f"Accelerometer: X={accel[0]:.2f}g, Y={accel[1]:.2f}g, Z={accel[2]:.2f}g")
            else:
                self.log.warning("Failed to read accelerometer data.")

            if gyro:
                self.log.info(f"Gyroscope: X={gyro[0]:.2f}°/s, Y={gyro[1]:.2f}°/s, Z={gyro[2]:.2f}°/s")
            else:
                self.log.warning("Failed to read gyroscope data.")

            if temp is not None:
                self.log.info(f"Temperature: {temp:.2f}°C")
            else:
                self.log.warning("Failed to read temperature data.")

            self.log.info("--- IMU Test Successful ---")
            return True
        except Exception as e:
            self.log.error("An error occurred during IMU test.", exc_info=True)
            return False

    async def test_adc(self) -> bool:
        """
        Tests the ADC (PCF8591) by reading battery voltage.
        """
        self.log.info("--- Starting ADC Test ---")
        adc = await self.factory.get_adc()

        if not adc or not adc.is_available():
            self.log.error("ADC (PCF8591) is not available.")
            return False

        try:
            self.log.info("Reading ADC data...")
            voltage = await adc.read_battery_voltage(channel=0)
            if voltage is not None:
                self.log.info(f"Battery Voltage: {voltage:.2f}V")
            else:
                self.log.warning("Failed to read battery voltage.")

            self.log.info("--- ADC Test Successful ---")
            return True
        except Exception as e:
            self.log.error("An error occurred during ADC test.", exc_info=True)
            return False

    async def test_buzzer(self) -> bool:
        """
        Tests the buzzer by playing a short sound.
        """
        self.log.info("--- Starting Buzzer Test ---")
        buzzer = await self.factory.get_buzzer()

        if not buzzer or not buzzer.is_available():
            self.log.error("Buzzer is not available.")
            return False

        try:
            self.log.info("Playing a sound with the buzzer.")
            buzzer.on()
            await asyncio.sleep(0.5)
            buzzer.off()
            self.log.info("--- Buzzer Test Successful ---")
            return True
        except Exception as e:
            self.log.error("An error occurred during buzzer test.", exc_info=True)
            return False


async def main():
    """
    Main function to parse arguments and run hardware tests.
    """
    parser = argparse.ArgumentParser(
        description="Unified hardware test script for the Hexapod robot.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--all", action="store_true", help="Run all hardware tests.")
    parser.add_argument("--led", action="store_true", help="Test the LED strip.")
    parser.add_argument("--servo", action="store_true", help="Test the servos.")
    parser.add_argument("--imu", action="store_true", help="Test the IMU (MPU6050).")
    parser.add_argument("--adc", action="store_true", help="Test the ADC (PCF8591).")
    parser.add_argument("--buzzer", action="store_true", help="Test the buzzer.")
    args = parser.parse_args()

    factory = None
    tester = None

    # Helper function for interactive mode
    async def run_test_interactively(test_name: str, coro: Coroutine[Any, Any, bool]):
        nonlocal test_results
        result = await coro
        test_results[test_name] = result
        status = "✅ PASS" if result else "❌ FAIL"
        log.info(f"--> Test '{test_name.upper()}' finished with status: {status}")

    # Interactive mode
    if not any(vars(args).values()):
        log.info("--- Interactive Hardware Test Mode ---")
        factory = get_hardware_factory()
        tester = HardwareTester(factory)
        test_coroutines = {
            "led": tester.test_leds,
            "servo": tester.test_servos,
            "imu": tester.test_imu,
            "adc": tester.test_adc,
            "buzzer": tester.test_buzzer,
        }

        while True:
            print("\nAvailable tests:")
            print("  1: Test LEDs")
            print("  2: Test Servos")
            print("  3: Test IMU")
            print("  4: Test ADC")
            print("  5: Test Buzzer")
            print("  a: Run all tests")
            print("  q: Quit")

            choice = input("Enter your choice: ").strip().lower()

            test_results = {}
            if choice == '1':
                await run_test_interactively('led', test_coroutines['led']())
            elif choice == '2':
                await run_test_interactively('servo', test_coroutines['servo']())
            elif choice == '3':
                await run_test_interactively('imu', test_coroutines['imu']())
            elif choice == '4':
                await run_test_interactively('adc', test_coroutines['adc']())
            elif choice == '5':
                await run_test_interactively('buzzer', test_coroutines['buzzer']())
            elif choice == 'a':
                for name, coro_func in test_coroutines.items():
                    await run_test_interactively(name, coro_func())
            elif choice == 'q':
                break
            else:
                log.warning("Invalid choice, please try again.")

        if factory:
            await factory.cleanup_all()
        return
    try:
        log.info("Initializing hardware factory...")
        factory = get_hardware_factory()
        tester = HardwareTester(factory)

        test_results: Dict[str, bool] = {}
        test_coroutines: Dict[str, Coroutine[Any, Any, bool]] = {
            "led": tester.test_leds(),
            "servo": tester.test_servos(),
            "imu": tester.test_imu(),
            "adc": tester.test_adc(),
            "buzzer": tester.test_buzzer(),
        }

        tasks_to_run: Dict[str, Coroutine[Any, Any, bool]] = {}
        if args.all:
            tasks_to_run = test_coroutines
        else:
            for test_name, coroutine in test_coroutines.items():
                if getattr(args, test_name):
                    tasks_to_run[test_name] = coroutine

        for test_name, coro in tasks_to_run.items():
            result = await coro
            test_results[test_name] = result

        # Summary
        log.info("--- Test Summary ---")
        for name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            log.info(f"{name.upper():.<15} {status}")

        if all(test_results.values()):
            log.info("All selected tests passed successfully!")
        else:
            log.warning("Some tests failed.")

    except Exception as e:
        log.error("An unexpected error occurred in main.", exc_info=True)
    finally:
        if factory:
            log.info("Cleaning up hardware resources...")
            await factory.cleanup_all()
            log.info("Cleanup complete.")


if __name__ == "__main__":
    asyncio.run(main())
