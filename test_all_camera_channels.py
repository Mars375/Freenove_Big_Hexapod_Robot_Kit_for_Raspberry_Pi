#!/usr/bin/env python3
"""Test ALL servo channels to find camera"""
import sys
from pathlib import Path

legacy_path = Path(__file__).parent / "legacy" / "Code" / "Server"
sys.path.insert(0, str(legacy_path))

from servo import Servo
import time

servo = Servo()

print("Testing ALL servo channels...")
print("Watch the robot carefully and note which servos move!")
print("")

# Test TOUS les channels (0-31)
for channel in range(32):
    try:
        print(f"\n=== Testing channel {channel} ===")
        print(f"Current position -> 90°")
        servo.set_servo_angle(channel, 90)
        time.sleep(1)
        
        print(f"Moving to 45°...")
        servo.set_servo_angle(channel, 45)
        time.sleep(1)
        
        print(f"Moving to 135°...")
        servo.set_servo_angle(channel, 135)
        time.sleep(1)
        
        print(f"Back to 90°")
        servo.set_servo_angle(channel, 90)
        time.sleep(1)
        
        response = input(f"Channel {channel}: Did CAMERA move? (y/n or 'q' to quit): ")
        if response.lower() == 'y':
            print(f"✓ CAMERA FOUND on channel {channel}!")
        elif response.lower() == 'q':
            break
            
    except Exception as e:
        print(f"Channel {channel} error: {e}")

print("\nTest complete!")
