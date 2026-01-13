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
