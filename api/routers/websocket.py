"""
WebSocket endpoints for real-time streaming.
Provides video stream and sensor data streaming.
"""
import asyncio
from datetime import datetime, timezone
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from core.config import settings
from core.logger import get_logger
from core.robot_controller import get_robot_controller, initialize_robot

logger = get_logger(__name__)
router = APIRouter()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Unified WebSocket endpoint for robot control and telemetry.
    Expects command JSON from client and streams telemetry data.
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("websocket.connected", client=websocket.client)
    
    robot = await initialize_robot()
    
    # Function states
    sonar_enabled = True
    camera_enabled = True
    face_recognition_enabled = False
    
    # Task for streaming telemetry data back to client
    async def stream_telemetry():
        try:
            nonlocal sonar_enabled
            while True:
                try:
                    # Use current robot state
                    distance = 0
                    if sonar_enabled:
                        distance = await robot.sensors.get_ultrasonic_distance()
                    
                    battery = await robot.sensors.get_battery_voltage()
                    
                    # App.jsx expects type "telemetry" with ultrasonic, battery, roll, pitch, yaw
                    state = {
                        "type": "telemetry",
                        "ultrasonic": distance,
                        "battery": battery,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    await websocket.send_json(state)
                except Exception as loop_e:
                    logger.warning("websocket.telemetry_loop_error", error=str(loop_e))
                
                await asyncio.sleep(0.5)  # Update at 2 Hz
        except Exception as e:
            logger.debug("websocket.telemetry_stream_stopped", error=str(e))

    telemetry_task = asyncio.create_task(stream_telemetry())
    
    try:
        while True:
            # Receive commands from the client
            data = await websocket.receive_json()
            cmd = data.get("cmd")
            if not cmd:
                continue
                
            logger.debug("websocket.command_received", command=cmd, data=data)
            
            try:
                if cmd == "move":
                    await robot.movement.move(
                        mode=data.get("mode", "custom"),
                        x=int(data.get("x", 0)),
                        y=int(data.get("y", 0)),
                        speed=int(data.get("speed", 5)),
                        angle=int(data.get("angle", 0))
                    )
                elif cmd == "stop":
                    await robot.movement.stop()
                elif cmd == "attitude":
                    await robot.movement.set_attitude(
                        roll=float(data.get("roll", 0)),
                        pitch=float(data.get("pitch", 0)),
                        yaw=float(data.get("yaw", 0))
                    )
                elif cmd == "position":
                    await robot.movement.set_position(
                        x=float(data.get("x", 0)),
                        y=float(data.get("y", 0)),
                        z=float(data.get("z", 0))
                    )
                elif cmd == "stand":
                    await robot.movement.stand()
                elif cmd == "relax":
                    enabled = data.get("enabled", True)
                    if enabled:
                        await robot.movement.relax()
                    else:
                        await robot.movement.stand()
                elif cmd == "balance":
                    enabled = data.get("enabled", False)
                    await robot.movement.set_balance_mode(enabled)
                elif cmd == "calibrate":
                    step = int(data.get("step", 0))
                    await robot.movement.calibrate(step)
                elif cmd == "sonar":
                    sonar_enabled = data.get("enabled", True)
                    logger.info("websocket.sonar_toggle", enabled=sonar_enabled)
                elif cmd == "camera_toggle":
                    camera_enabled = data.get("enabled", True)
                    # Here we could call robot.camera.stop() or start()
                    logger.info("websocket.camera_toggle", enabled=camera_enabled)
                elif cmd == "face":
                    face_recognition_enabled = data.get("enabled", False)
                    logger.info("websocket.face_recognition_toggle", enabled=face_recognition_enabled)
                elif cmd == "height":
                    height = float(data.get("value", -100.0))
                    robot.movement.body_height = height
                    await robot.movement.stand()
                    logger.info("websocket.height_updated", height=height)
                elif cmd == "buzzer":
                    enabled = data.get("enabled", False)
                    if enabled:
                        await robot.buzzer.beep(0.1)
                elif cmd == "camera":
                    await robot.camera.rotate(
                        horizontal=int(data.get("horizontal", 1500)),
                        vertical=int(data.get("vertical", 1500))
                    )
                elif cmd == "led":
                    await robot.leds.set_color(
                        index=int(data.get("index", -1)),
                        r=int(data.get("r", 0)),
                        g=int(data.get("g", 0)),
                        b=int(data.get("b", 0))
                    )
            except Exception as e:
                logger.error("websocket.command_error", command=cmd, error=str(e))
                await websocket.send_json({
                    "type": "error",
                    "message": f"Command {cmd} failed: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info("websocket.disconnected", client=websocket.client)
    except Exception as e:
        logger.error("websocket.error", error=str(e))
    finally:
        telemetry_task.cancel()
        if websocket in active_connections:
            active_connections.remove(websocket)


@router.websocket("/video")
async def websocket_video(websocket: WebSocket):
    """
    Legacy WebSocket endpoint for video streaming.
    Included for backward compatibility.
    """
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            # In a better system, this would come from a shared buffer
            from core.hardware.factory import get_hardware_factory
            camera = await get_hardware_factory().get_camera()
            frame = await camera.get_frame()
            if frame:
                import base64
                await websocket.send_json({
                    "type": "video_frame",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "frame": base64.b64encode(frame).decode('utf-8')
                })
            await asyncio.sleep(1/30)
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


@router.get("/test")
async def websocket_test_page():
    """Test page for WebSocket connections."""
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Test</title>
        </head>
        <body>
            <h1>WebSocket Streaming Test</h1>
            <div id="status">Connecting...</div>
            <div id="data"></div>
            
            <script>
                const ws = new WebSocket("ws://localhost:8000/api/v1/ws/sensors");
                
                ws.onopen = () => {
                    document.getElementById("status").innerHTML = "Connected";
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    document.getElementById("data").innerHTML = JSON.stringify(data, null, 2);
                };
                
                ws.onclose = () => {
                    document.getElementById("status").innerHTML = "Disconnected";
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
