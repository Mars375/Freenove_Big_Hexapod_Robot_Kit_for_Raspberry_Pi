"""
Basic Walking Validaton
-----------------------
Tests the MovementController integration (IK + Gait + Servos).
"""
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.hardware.factory import get_hardware_factory
from core.hardware.movement import MovementController

async def main():
    print("Initializing Hexapod...")
    factory = get_hardware_factory()
    
    try:
        servo_ctrl = await factory.create_servo_controller()
    except Exception as e:
        print(f"Failed to connect to servos: {e}")
        return

    movement = MovementController(servo_ctrl)
    await movement.initialize()
    
    print("Standing up...")
    await movement.stand()
    await asyncio.sleep(2)
    
    print("Walking Forward (Tripod Gait)...")
    # Walk forward for 3 seconds
    await movement.move("forward", 0, 0, speed=5, angle=0)
    await asyncio.sleep(3)
    
    print("Stopping...")
    await movement.stop()
    
    print("Cleanup...")
    await factory.cleanup_all()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
