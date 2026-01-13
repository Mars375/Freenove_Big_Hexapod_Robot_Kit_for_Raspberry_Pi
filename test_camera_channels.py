#!/usr/bin/env python3
"""Test camera servo channels"""
import sys
from pathlib import Path

legacy_path = Path(__file__).parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from servo import Servo
import time

servo = Servo()

print("Testing servo channels for camera...")
print("Testing will move servos from 0 to 180 degrees on each channel")
print("")

# Test channels that might be camera (typically 0-1 or higher channels like 24-31)
test_channels = [0, 1, 24, 25, 26, 27, 28, 29, 30, 31]

for channel in test_channels:
    try:
        print(f"Testing channel {channel}...")
        
        # Center position
        servo.set_servo_angle(channel, 90)
        time.sleep(0.5)
        
        # Move left/down
        servo.set_servo_angle(channel, 45)
        time.sleep(0.5)
        
        # Move right/up
        servo.set_servo_angle(channel, 135)
        time.sleep(0.5)
        
        # Return to center
        servo.set_servo_angle(channel, 90)
        time.sleep(0.5)
        
        print(f"  Channel {channel} tested successfully")
        input(f"  Did the camera move? (Press Enter to continue)")
        
    except Exception as e:
        print(f"  Channel {channel} failed: {e}")

print("\nTest complete!")
