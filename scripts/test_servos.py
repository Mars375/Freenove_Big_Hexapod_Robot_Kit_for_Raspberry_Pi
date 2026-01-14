"""
Simple Servo Test Script
------------------------
Steps through each servo to verify wiring and movement.
Run this to confirm Phase 0 fixes.
"""
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.hardware.factory import get_hardware_factory
from core.hardware.movement import LEGS

async def main():
    print("Initializing components...")
    factory = get_hardware_factory()
    
    # Initialize Servo Controller (Dual Board)
    try:
        servos = await factory.create_servo_controller()
    except Exception as e:
        print(f"FATAL: Could not init servos: {e}")
        return

    print("Status:", servos.get_status())
    
    print("\n--- STANDING ---")
    # Reset all to 90
    await servos.reset_async()
    await asyncio.sleep(1)
    
    print("\n--- TESTING INDIVIDUAL LEGS ---")
    
    # Iterate through leg mapping from movement.py
    # Reconstruct mapping locally to be sure or use imported LEGS if accessible
    # LEGS is a dict in movement.py, let's just inspect it via the MovementController if possible
    # or just iterate 0-31 manually first time.
    
    print("Wiggling all 32 channels (0-31)...")
    for channel in range(32):
        print(f"Testing Channel {channel}...", end="", flush=True)
        try:
            # Wiggle 80 -> 100 -> 90
            await servos.set_angle_async(channel, 80)
            await asyncio.sleep(0.1)
            await servos.set_angle_async(channel, 100)
            await asyncio.sleep(0.1)
            await servos.set_angle_async(channel, 90)
            print(" OK")
        except Exception as e:
            print(f" FAIL ({e})")
        
        await asyncio.sleep(0.1)

    print("\n--- TESTING LEG MAPPING ---")
    # If we import MovementController we can verify logical leg mapping
    from core.hardware.movement import MovementController
    movement = MovementController(servos)
    
    # Print understood mapping
    for leg in movement.legs:
        print(f"Leg {leg.id} pins: {leg.servo_pins}")
        
    print("\nTest Complete. If all servos moved, hardware is good!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
