#!/usr/bin/env python3
"""Test hexapod walking with the modern movement controller.

This script tests:
1. Standing up
2. Walking forward (tripod gait)
3. Turning
4. Wave gait
5. Body attitude control
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_settings
from core.hardware.factory import get_hardware_factory
from core.hardware.movement import MovementController


async def main():
    """Run walking test sequence."""
    print("=" * 60)
    print("HEXAPOD WALKING TEST")
    print("=" * 60)
    print()
    
    # Initialize hardware
    print("Initializing hardware...")
    settings = get_settings()
    factory = get_hardware_factory(settings)
    
    try:
        # Create servo controller and movement controller
        servo = await factory.create_servo_controller()
        movement = MovementController(servo_controller=servo)
        await movement.initialize()
        
        print("Hardware initialized!")
        print()
        
        # Test 1: Stand
        print("[TEST 1] Standing up...")
        await movement.stand()
        print("Standing - OK")
        await asyncio.sleep(1)
        
        # Test 2: Walk forward (tripod gait)
        print()
        print("[TEST 2] Walking FORWARD (tripod gait)...")
        await movement.run_gait(
            gait_type="1",  # Tripod
            x=0,            # No lateral
            y=25,           # Forward
            speed=5,        # Medium speed
            angle=0,        # No rotation
            duration=3.0    # 3 seconds
        )
        print("Forward walk - OK")
        
        # Return to stand
        await movement.stand()
        await asyncio.sleep(0.5)
        
        # Test 3: Turn left
        print()
        print("[TEST 3] Turning LEFT...")
        await movement.run_gait(
            gait_type="1",
            x=0,
            y=0,
            speed=5,
            angle=15,       # Turn left
            duration=2.0
        )
        print("Turn left - OK")
        
        await movement.stand()
        await asyncio.sleep(0.5)
        
        # Test 4: Wave gait (optional - slower but more stable)
        print()
        print("[TEST 4] Walking FORWARD (wave gait)...")
        await movement.run_gait(
            gait_type="2",  # Wave
            x=0,
            y=20,
            speed=5,
            angle=0,
            duration=5.0
        )
        print("Wave gait - OK")
        
        await movement.stand()
        await asyncio.sleep(0.5)
        
        # Test 5: Body attitude
        print()
        print("[TEST 5] Testing body attitude...")
        
        print("  - Roll left...")
        await movement.set_attitude(roll=10, pitch=0, yaw=0)
        await asyncio.sleep(0.5)
        
        print("  - Roll right...")
        await movement.set_attitude(roll=-10, pitch=0, yaw=0)
        await asyncio.sleep(0.5)
        
        print("  - Pitch forward...")
        await movement.set_attitude(roll=0, pitch=10, yaw=0)
        await asyncio.sleep(0.5)
        
        print("  - Pitch back...")
        await movement.set_attitude(roll=0, pitch=-10, yaw=0)
        await asyncio.sleep(0.5)
        
        print("  - Return to neutral...")
        await movement.stand()
        print("Attitude control - OK")
        
        print()
        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print()
        print("Cleaning up...")
        await factory.cleanup_all()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
