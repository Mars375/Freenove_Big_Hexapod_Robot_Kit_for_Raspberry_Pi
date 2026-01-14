#!/usr/bin/env python3
"""Test script for Camera driver."""
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
    print("CAMERA TEST")
    print("=" * 60)
    
    settings = get_settings()
    factory = get_hardware_factory(settings)
    
    try:
        print("\nInitializing camera...")
        camera = await factory.get_camera()
        
        status = camera.get_health()
        print(f"Driver status: {status}")
        
        if not status["healthy"]:
            print("ERROR: Camera driver not healthy!")
            return
            
        print("\nStarting stream for 5 seconds...")
        await camera.start_streaming()
        
        for i in range(5, 0, -1):
            print(f"Streaming... {i}s", end="\r")
            await asyncio.sleep(1)
            
        print("\nCapturing a frame...")
        frame = await camera.get_frame()
        print(f"Captured frame size: {len(frame)} bytes")
        
        if len(frame) > 0:
            with open("test_frame.jpg", "wb") as f:
                f.write(frame)
            print("Frame saved to test_frame.jpg")
        
        await camera.stop_streaming()
        print("\nTest completed successfully!")
            
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
