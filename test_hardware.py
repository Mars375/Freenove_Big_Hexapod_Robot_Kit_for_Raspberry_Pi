#!/usr/bin/env python3
"""Test de tous les composants hardware"""
import asyncio
import sys
sys.path.append('.')

from core.hardware.factory import get_hardware_factory

async def audit_hardware():
    print("🔧 AUDIT HARDWARE")
    print("=" * 50)
    
    factory = get_hardware_factory()
    
    # Test Servos
    print("\n🦾 SERVOS (PCA9685):")
    try:
        servos = await factory.create_servo_controller()
        status = servos.get_status()
        print(f"  ✅ Status: {status}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test Movement
    print("\n🦿 MOVEMENT CONTROLLER:")
    try:
        movement = await factory.get_movement_controller()
        print(f"  ✅ Initialized: True")
        print(f"  ✅ Legs: {len(movement.legs)}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test Camera
    print("\n📸 CAMERA:")
    try:
        camera = await factory.get_camera()
        print(f"  ✅ Camera: {type(camera).__name__}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test Sensors
    print("\n🔋 SENSORS:")
    try:
        sensors = await factory.get_sensors()
        battery = await sensors.read_battery()
        print(f"  ✅ Battery: {battery['voltage']}V ({battery['percentage']}%)")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test Ultrasonic
    print("\n📡 ULTRASONIC:")
    try:
        ultrasonic = await factory.get_ultrasonic()
        distance = await ultrasonic.read_distance()
        print(f"  ✅ Distance: {distance}cm")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # Test LEDs
    print("\n💡 LEDS:")
    try:
        leds = await factory.get_led_controller()
        print(f"  ✅ LEDs: {type(leds).__name__}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(audit_hardware())
