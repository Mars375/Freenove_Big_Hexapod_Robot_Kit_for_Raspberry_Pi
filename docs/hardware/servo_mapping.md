# Servo Mapping & Hardware Configuration

## Hardware Architecture

The Freenove Big Hexapod Robot uses a **Dual PCA9685** architecture for controlling 18+ servos.

### I2C Addressing
- **Board 1 (Low)**: Address `0x41`
  - Controls logical channels 0-15
  - Physical connection: Right side legs + Camera?
- **Board 0 (High)**: Address `0x40`
  - Controls logical channels 16-31
  - Physical connection: Left side legs + Camera?

### Pin Assignments

| Leg | ID | Position | Coxa (C) | Femur (F) | Tibia (T) | Board |
|-----|----|----------|----------|-----------|-----------|-------|
| 0   | RF | Right Front | 15 | 14 | 13 | #1 (0x41) |
| 1   | RM | Right Mid | 12 | 11 | 10 | #1 (0x41) |
| 2   | RR | Right Rear | 9 | 8 | 31* | Mixed (#1 & #0) |
| 3   | LR | Left Rear | 22 | 23 | 27 | #0 (0x40) |
| 4   | LM | Left Mid | 19 | 20 | 21 | #0 (0x40) |
| 5   | LF | Left Front | 16 | 17 | 18 | #0 (0x40) |

> **Note on Leg 2 Tibia**: 
> Pin `31` maps to **Channel 15 on Board #0 (0x40)**.
> (31 - 16 = 15).

### Virtual Channel Logic
The software `PCA9685ServoController` abstracts the two boards into a single continuous channel space (0-31):
- **Input 0-15**: Routed to Board #1 (0x41) -> Channel 0-15
- **Input 16-31**: Routed to Board #0 (0x40) -> Channel (Input - 16)

## Other Components
- **Buzzer**: GPIO 17 (Active Buzzer)
- **LEDs**: SPI (MOSI/SCLK) or dedicated LED strip controller.
- **Ultrasonic**: HC-SR04 (Trigger/Echo pins)
- **IMU**: MPU6050 @ `0x68`

## Troubleshooting
If servos are swapped:
1. Verify `I2C` addresses using `i2cdetect -y 1`.
2. Check `LEGS` dictionary in `core/hardware/movement.py`.
