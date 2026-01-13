"""
WebSocket endpoints for real-time streaming.
Provides video stream and sensor data streaming.
"""
import asyncio
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from core.config import settings
from core.logger import get_logger
from core.robot_controller import get_robot_controller

logger = get_logger(__name__)
router = APIRouter()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/video")
async def websocket_video(websocket: WebSocket):
    """
    WebSocket endpoint for video streaming.
    
    Streams camera frames to connected clients.
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("websocket.video.connected", client=websocket.client)
    
    try:
        while True:
            # TODO: Capture frame from camera
            # For now, send mock data
            await websocket.send_json({
                "type": "video_frame",
                "timestamp": "2026-01-13T16:00:00Z",
                "frame": "base64_encoded_frame_here"
            })
            await asyncio.sleep(1/30)  # 30 FPS
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("websocket.video.disconnected", client=websocket.client)
    except Exception as e:
        logger.error("websocket.video.error", error=str(e))
        active_connections.remove(websocket)


@router.websocket("/sensors")
async def websocket_sensors(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sensor data.
    
    Streams sensor data (IMU, ultrasonic, battery) to connected clients.
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("websocket.sensors.connected", client=websocket.client)
    
    robot = get_robot_controller()
    
    try:
        while True:
            # Send current robot state
            state = robot.get_state()
            await websocket.send_json({
                "type": "sensor_data",
                "timestamp": "2026-01-13T16:00:00Z",
                "data": state
            })
            await asyncio.sleep(0.1)  # 10 Hz
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("websocket.sensors.disconnected", client=websocket.client)
    except Exception as e:
        logger.error("websocket.sensors.error", error=str(e))
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
