#!/usr/bin/env python3
"""Test script for Ultrasonic Sensor driver.

Verifies:
1. Driver initialization
2. HardwareFactory integration
3. Distance measurement
"""
import asyncio
import sys
import os
import structlog

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_settings
from core.hardware.factory import get_hardware_factory

logger = structlog.get_logger()

async def main():
    print("=" * 60)
    print("ULTRASONIC SENSOR TEST")
    print("=" * 60)
    
    settings = get_settings()
    factory = get_hardware_factory(settings)
    
    try:
        print("\nInitializing hardware...")
        # Get ultrasonic driver (default pins: Trig=27, Echo=22)
        ultrasonic = await factory.get_ultrasonic()
        
        status = ultrasonic.get_health()
        print(f"Driver status: {status}")
        
        if not status["healthy"]:
            print("ERROR: Driver not healthy!")
            return
            
        print("\nStarting measurement loop (Press Ctrl+C to stop)...")
        print("-" * 40)
        
        while True:
            distance = await ultrasonic.get_distance()
            
            if distance is not None:
                print(f"Distance: {distance:>5.1f} cm", end="\r")
            else:
                print("Distance: --.- cm (Error)", end="\r")
                
            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        await factory.cleanup_all()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
