"""
Main FastAPI application.
Provides REST API endpoints for robot control and monitoring.
"""
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import buzzer, camera, leds, movement, sensors, websocket
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    # Startup
    logger.info("app.startup", version=settings.app_version, environment=settings.environment)
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Freenove Big Hexapod Robot - Modernized API",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include all routers
    app.include_router(movement.router, prefix="/api/v1/movement", tags=["movement"])
    app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["sensors"])
    app.include_router(camera.router, prefix="/api/v1/camera", tags=["camera"])
    app.include_router(leds.router, prefix="/api/v1/leds", tags=["leds"])
    app.include_router(buzzer.router, prefix="/api/v1/buzzer", tags=["buzzer"])
    app.include_router(websocket.router, prefix="/api/v1/ws", tags=["websocket"])
    
    return app


app = create_app()


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with basic info and available endpoints."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "robot": settings.robot_name,
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "movement": "/api/v1/movement",
            "sensors": "/api/v1/sensors",
            "camera": "/api/v1/camera",
            "leds": "/api/v1/leds",
            "buzzer": "/api/v1/buzzer"
        }
    }


@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint for monitoring and Orion Guardian integration."""
    logger.debug("health.check")
    
    return {
        "status": "healthy",
        "robot": settings.robot_name,
        "version": settings.app_version,
        "camera_enabled": settings.camera_enabled,
        "imu_enabled": settings.imu_enabled,
        "ultrasonic_enabled": settings.ultrasonic_enabled,
    }


@app.get("/metrics")
async def metrics() -> JSONResponse:
    """Prometheus-compatible metrics endpoint."""
    metrics_text = f"""# HELP robot_info Robot information
# TYPE robot_info gauge
robot_info{{name="{settings.robot_name}",version="{settings.app_version}"}} 1

# HELP robot_health Robot health status
# TYPE robot_health gauge
robot_health 1
"""
    return JSONResponse(content={"metrics": metrics_text})


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
