"""FastAPI server for Tachikoma robot control"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tachikoma.core.config import settings
from tachikoma.core.logger import get_logger
from tachikoma.core.robot_controller import initialize_robot, get_robot_controller
from tachikoma.api.routers import movement, leds, sensors, camera, buzzer, advanced

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize robot on startup"""
    logger.info("api.starting")
    try:
        robot = await initialize_robot()
        logger.info("api.robot_ready")
        yield
    finally:
        logger.info("api.shutting_down")
        robot = get_robot_controller()
        if robot:
            await robot.movement.stop()


app = FastAPI(
    title="Tachikoma API",
    description="🤖 Hexapod Robot Control API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, restreindre aux IPs autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(movement.router, prefix="/api/movement", tags=["Movement"])
app.include_router(leds.router, prefix="/api/leds", tags=["LEDs"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(camera.router, prefix="/api/camera", tags=["Camera"])
app.include_router(buzzer.router, prefix="/api/buzzer", tags=["Buzzer"])
app.include_router(advanced.router, prefix="/api/advanced", tags=["Advanced"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Tachikoma API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check"""
    robot = get_robot_controller()
    return {
        "status": "healthy",
        "hardware_available": robot.is_hardware_available if robot else False
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "tachikoma.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
