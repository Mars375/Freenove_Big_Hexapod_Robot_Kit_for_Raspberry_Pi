"""
Robot controller for managing hardware communication.
Handles TCP connection to robot and state management.
"""
import asyncio
from typing import Optional

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class RobotController:
    """
    Main robot controller managing hardware communication and state.
    
    This controller acts as a bridge between the API and the actual robot hardware.
    """
    
    def __init__(self):
        """Initialize robot controller."""
        self.connected = False
        self.tcp_writer: Optional[asyncio.StreamWriter] = None
        self.tcp_reader: Optional[asyncio.StreamReader] = None
        
        # Robot state
        self.state = {
            "moving": False,
            "position": {"x": 0, "y": 0, "z": 0},
            "attitude": {"roll": 0, "pitch": 0, "yaw": 0},
            "battery": {"voltage": 0.0, "percentage": 0},
            "camera_angle": {"horizontal": 0, "vertical": 0}
        }
        
        logger.info("robot_controller.initialized")
    
    async def connect(self, host: str = "localhost", port: int = 5002) -> bool:
        """
        Connect to robot TCP server.
        
        Args:
            host: Robot IP address
            port: Robot command port
            
        Returns:
            True if connection successful
        """
        try:
            self.tcp_reader, self.tcp_writer = await asyncio.open_connection(host, port)
            self.connected = True
            logger.info("robot_controller.connected", host=host, port=port)
            return True
        except Exception as e:
            logger.error("robot_controller.connect.failed", error=str(e))
            self.connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from robot."""
        if self.tcp_writer:
            self.tcp_writer.close()
            await self.tcp_writer.wait_closed()
            self.connected = False
            logger.info("robot_controller.disconnected")
    
    async def send_command(self, command: str) -> bool:
        """
        Send command to robot.
        
        Args:
            command: Command string (e.g., "CMD_MOVE#motion#10#5#7#0")
            
        Returns:
            True if command sent successfully
        """
        if not self.connected:
            logger.warning("robot_controller.send.not_connected")
            return False
        
        try:
            command_bytes = (command + "\n").encode()
            self.tcp_writer.write(command_bytes)
            await self.tcp_writer.drain()
            logger.debug("robot_controller.command_sent", command=command)
            return True
        except Exception as e:
            logger.error("robot_controller.send.error", command=command, error=str(e))
            return False
    
    def get_state(self) -> dict:
        """
        Get current robot state.
        
        Returns:
            Current state dictionary
        """
        return self.state.copy()
    
    def update_state(self, key: str, value: any) -> None:
        """
        Update robot state.
        
        Args:
            key: State key (e.g., "position", "battery")
            value: New value
        """
        self.state[key] = value
        logger.debug("robot_controller.state_updated", key=key, value=value)


# Global robot controller instance
_robot_controller: Optional[RobotController] = None


def get_robot_controller() -> RobotController:
    """
    Get or create robot controller singleton.
    
    Returns:
        Robot controller instance
    """
    global _robot_controller
    if _robot_controller is None:
        _robot_controller = RobotController()
    return _robot_controller
