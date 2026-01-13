# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-13

### 🎉 Major Release - Complete Rewrite

#### Added
- **Modern Architecture**: Complete restructure with modular design
- **FastAPI REST API**: Modern async web framework with automatic docs
- **Structured Logging**: JSON logging with structlog for production monitoring
- **Configuration Management**: Pydantic Settings with environment variables
- **Automated Testing**: pytest with 98% code coverage
- **Development Tools**: Makefile with common commands
- **Health Check Endpoint**: /health for monitoring and orchestration
- **Metrics Endpoint**: /metrics Prometheus-compatible
- **CORS Support**: Configured for web applications
- **Hot Reload**: Development server with automatic restart
- **Type Hints**: Full typing support with mypy

#### Changed
- **Architecture**: Moved from monolithic PyQt5 to microservices design
- **Threading**: Replaced with asyncio for better performance
- **Configuration**: Externalized from code to environment variables
- **Logging**: Upgraded from print() to structured logging
- **Dependencies**: Modern packages with Poetry management
- **Testing**: Added comprehensive test suite

#### Project Structure

    api/          - REST API endpoints
    core/         - Core modules (config, logger)
    features/     - Modular features
    tests/        - Unit and integration tests
    config/       - Configuration files
    legacy/       - Original Freenove code (preserved)

#### Technical Stack
- Python 3.11+
- FastAPI 0.109+
- Pydantic 2.5+
- Structlog 24.1+
- Pytest 7.4+
- Poetry 2.2+

### Migration Notes

The original code is preserved in legacy/Code/ for reference.

For migration from v1.x to v2.0:
1. Update configuration to use .env file
2. Use REST API endpoints instead of direct TCP
3. Update imports to new module structure
4. Review logging format (now JSON in production)

---

## [1.x] - Legacy Versions

See git history for previous versions (original Freenove code).

Original repository: https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi

## [2.1.0] - 2026-01-13

### 🎉 Phase 2 Complete - Full REST API

#### Added
- **Movement Router**: 5 endpoints for robot locomotion control
  - POST /api/v1/movement/move - Move robot with mode, speed, angle
  - POST /api/v1/movement/stop - Emergency stop
  - POST /api/v1/movement/attitude - Control roll, pitch, yaw
  - POST /api/v1/movement/position - Control x, y, z position
  - GET /api/v1/movement/status - Get movement state

- **Sensors Router**: 4 endpoints for sensor data
  - GET /api/v1/sensors/imu - IMU accelerometer and gyroscope
  - GET /api/v1/sensors/ultrasonic - Distance measurement
  - GET /api/v1/sensors/battery - Battery voltage and percentage
  - GET /api/v1/sensors/all - Combined sensor data

- **Camera Router**: 3 endpoints for camera control
  - POST /api/v1/camera/rotate - Rotate camera horizontally/vertically
  - GET /api/v1/camera/config - Get camera configuration
  - POST /api/v1/camera/config - Update camera settings

- **LEDs Router**: 2 endpoints for LED control
  - POST /api/v1/leds/mode - Set LED mode (off/solid/chase/blink/breathing/rainbow)
  - POST /api/v1/leds/color - Set RGB color

- **Buzzer Router**: 1 endpoint for buzzer control
  - POST /api/v1/buzzer/beep - Control buzzer on/off with duration

- **Pydantic Models**: Complete request/response validation
  - MoveRequest, AttitudeRequest, PositionRequest
  - IMUData, UltrasonicData, BatteryData, AllSensorsData
  - CameraRotateRequest, CameraConfigResponse
  - LEDModeRequest, LEDColorRequest, LEDResponse
  - BuzzerRequest, BuzzerResponse

#### Changed
- Root endpoint now includes links to all API endpoints
- Datetime handling updated to use timezone-aware datetime.now(timezone.utc)

#### Tests
- Added 16 new integration tests for all routers
- Total: 26 tests with 89% code coverage
- All tests passing

#### Technical Details
- 15 new API endpoints
- 5 routers with proper error handling
- Complete OpenAPI documentation
- CORS configured for all endpoints


## [2.2.0] - 2026-01-13

### 🎉 Phase 3 Complete - Intelligence & Advanced Features

#### Added
- **Robot Controller Core**: Unified TCP communication and state management
- **WebSocket Streaming**: Real-time video and sensor data streaming
- **Obstacle Avoidance**: Intelligent autonomous navigation with 4-level distance analysis
- **Object Detection**: YOLOv8 integration placeholder for computer vision
- **QR Scanner**: QR code detection and decoding from camera feed

#### Endpoints Added
- GET /api/v1/ws/video - WebSocket video stream
- GET /api/v1/ws/sensors - WebSocket sensor data
- GET /api/v1/ws/test - WebSocket test page
- GET /api/v1/advanced/obstacle-avoidance/analyze - Analyze obstacles
- GET /api/v1/advanced/vision/detect - Detect objects
- GET /api/v1/advanced/vision/scan-qr - Scan QR codes

#### Modules Added
- core/robot_controller.py - Main robot controller
- features/autonomous/obstacle_avoidance.py - Autonomous navigation
- features/vision/object_detection.py - Object detection
- features/vision/qr_scanner.py - QR code scanner
- api/routers/websocket.py - WebSocket endpoints
- api/routers/advanced.py - Advanced features endpoints

#### Tests
- Added 10+ new unit tests
- Tests for obstacle avoidance logic
- Tests for vision modules
- Tests for robot controller
- Total: 35+ tests

