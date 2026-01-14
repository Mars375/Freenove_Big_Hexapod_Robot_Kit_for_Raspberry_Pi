"""FastAPI server for Hexapod Web Interface."""
import asyncio
import io
import structlog
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from core.hardware.factory import get_hardware_factory
from core.config import get_settings

logger = structlog.get_logger()

app = FastAPI(title="Hexapod Control")

import os

# Initialize hardware factory
settings = get_settings()
factory = get_hardware_factory(settings)

# Paths for frontend distribution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# Setup templates and static files from the React build
templates = Jinja2Templates(directory=DIST_DIR)

if os.path.exists(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="static")
    # Serve PWA icons and manifest if they are in the root of dist
    app.mount("/pwa", StaticFiles(directory=DIST_DIR), name="pwa")
else:
    logger.warning("web_server.dist_not_found", path=DIST_DIR)

@app.on_event("startup")
async def startup_event():
    logger.info("web_server.startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("web_server.shutdown")
    await factory.cleanup_all()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
async def status():
    return {"status": "ok", "message": "Hexapod API is running"}

async def gen_frames():
    """Video streaming generator."""
    camera = await factory.get_camera()
    await camera.start_streaming()
    try:
        while True:
            frame = await camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            await asyncio.sleep(0.01) # Small sleep to prevent CPU hogging
    except Exception as e:
        logger.error("web_server.stream_error", error=str(e))
    finally:
        await camera.stop_streaming()

@app.get("/video_feed")
async def video_feed():
    """Video streaming route."""
    return StreamingResponse(gen_frames(),
                            media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("web_server.ws_connected")
    
    # Get movement controller
    servo = await factory.create_servo_controller()
    from core.hardware.movement import MovementController
    movement = MovementController(servo_controller=servo)
    await movement.initialize()
    
    # Get sensors for telemetry
    ultrasonic = await factory.get_ultrasonic()
    
    # Start telemetry loop
    telemetry_task = asyncio.create_task(send_telemetry(websocket, ultrasonic))
    
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("cmd")
            
            if command == "move":
                # { "cmd": "move", "mode": "forward", "speed": 10, "x": 0, "y": 25, "angle": 0 }
                mode = data.get("mode")
                speed = data.get("speed", 5)
                x = data.get("x", 0)
                y = data.get("y", 0)
                angle = data.get("angle", 0)
                await movement.move(mode=mode, speed=speed, x=x, y=y, angle=angle)
            elif command == "stop":
                await movement.stop()
            elif command == "stand":
                await movement.stand()
            elif command == "attitude":
                # { "cmd": "attitude", "roll": 0, "pitch": 10, "yaw": 0 }
                await movement.set_attitude(
                    roll=data.get("roll", 0),
                    pitch=data.get("pitch", 0),
                    yaw=data.get("yaw", 0)
                )
            elif command == "position":
                # { "cmd": "position", "x": 0, "y": 0, "z": 0 }
                await movement.set_position(
                    x=data.get("x", 0),
                    y=data.get("y", 0),
                    z=data.get("z", 0)
                )
                
    except WebSocketDisconnect:
        logger.info("web_server.ws_disconnected")
    except Exception as e:
        logger.error("web_server.ws_error", error=str(e))
    finally:
        telemetry_task.cancel()
        await movement.stop()

async def send_telemetry(websocket: WebSocket, ultrasonic):
    """Periodically send sensor data to client."""
    try:
        while True:
            distance = await ultrasonic.get_distance()
            await websocket.send_json({
                "type": "telemetry",
                "ultrasonic": distance,
                # Add battery, IMU here later
            })
            await asyncio.sleep(0.5)
    except Exception:
        pass
