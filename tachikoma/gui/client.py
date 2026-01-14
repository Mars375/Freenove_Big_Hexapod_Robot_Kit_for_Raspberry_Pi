"""
Tachikoma GUI Client - Remote control interface
Run this on your PC to connect to Tachikoma API
"""
import sys
import asyncio
import aiohttp
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QStatusBar, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QTimer
import signal

from tachikoma.core.logger import get_logger
from tachikoma.gui.widgets.movement_panel import MovementPanel
from tachikoma.gui.widgets.status_panel import StatusPanel
from tachikoma.gui.widgets.led_panel import LEDPanel

logger = get_logger(__name__)


class RemoteRobotController:
    """Remote robot controller via HTTP API"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.movement = RemoteMovementController(self)
        self.leds = RemoteLEDController(self)
        self.sensors = RemoteSensorController(self)
    
    async def initialize(self):
        """Initialize HTTP session"""
        timeout = aiohttp.ClientTimeout(total=5)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        try:
            async with self.session.get(f"{self.api_url}/health") as resp:
                if resp.status == 200:
                    logger.info("client.connected", url=self.api_url)
                    return True
        except Exception as e:
            logger.error("client.connection_failed", error=str(e))
            raise ConnectionError(f"Cannot connect to {self.api_url}")
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    @property
    def is_hardware_available(self) -> bool:
        return True


class RemoteMovementController:
    def __init__(self, robot: RemoteRobotController):
        self.robot = robot
        self.is_available = True
    
    async def forward(self, speed: int = 50):
        async with self.robot.session.post(
            f"{self.robot.api_url}/api/movement/forward",
            json={"speed": speed}
        ) as resp:
            return await resp.json()
    
    async def backward(self, speed: int = 50):
        async with self.robot.session.post(
            f"{self.robot.api_url}/api/movement/backward",
            json={"speed": speed}
        ) as resp:
            return await resp.json()
    
    async def turn_left(self, speed: int = 50):
        async with self.robot.session.post(
            f"{self.robot.api_url}/api/movement/turn_left",
            json={"speed": speed}
        ) as resp:
            return await resp.json()
    
    async def turn_right(self, speed: int = 50):
        async with self.robot.session.post(
            f"{self.robot.api_url}/api/movement/turn_right",
            json={"speed": speed}
        ) as resp:
            return await resp.json()
    
    async def stop(self):
        async with self.robot.session.post(
            f"{self.robot.api_url}/api/movement/stop"
        ) as resp:
            return await resp.json()


class RemoteLEDController:
    def __init__(self, robot: RemoteRobotController):
        self.robot = robot
        self.is_available = True
    
    async def set_color(self, r: int, g: int, b: int):
        async with self.robot.session.post(
            f"{self.robot.api_url}/api/leds/color",
            json={"r": r, "g": g, "b": b}
        ) as resp:
            return await resp.json()


class RemoteSensorController:
    def __init__(self, robot: RemoteRobotController):
        self.robot = robot
    
    async def get_battery_voltage(self):
        async with self.robot.session.get(
            f"{self.robot.api_url}/api/sensors/battery"
        ) as resp:
            return await resp.json()
    
    async def get_imu_data(self):
        async with self.robot.session.get(
            f"{self.robot.api_url}/api/sensors/imu"
        ) as resp:
            data = await resp.json()
            return {
                "pitch": data.get("pitch", 0),
                "roll": data.get("roll", 0),
                "yaw": data.get("yaw", 0)
            }
    
    async def get_distance(self):
        async with self.robot.session.get(
            f"{self.robot.api_url}/api/sensors/distance"
        ) as resp:
            data = await resp.json()
            return data.get("distance_cm", 0)


class TachikomaClientWindow(QMainWindow):
    """Client window for remote control"""
    
    def __init__(self):
        super().__init__()
        self.robot: Optional[RemoteRobotController] = None
        self.telemetry_timer: Optional[QTimer] = None
        
        self.init_ui()
        self.apply_dark_theme()
        QTimer.singleShot(100, self.connect_to_server)
    
    def init_ui(self):
        self.setWindowTitle("🤖 Tachikoma Remote Control")
        self.setGeometry(100, 100, 1200, 800)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Connecting...")
        
        self.status_widget = StatusPanel()
        self.tabs.addTab(self.status_widget, "📊 Status")
    
    def connect_to_server(self):
        ip, ok = QInputDialog.getText(
            self,
            "Connect to Tachikoma",
            "Enter Tachikoma IP address:",
            text="tachikoma.local"
        )
        
        if not ok or not ip:
            QMessageBox.critical(self, "Error", "No IP provided")
            sys.exit(1)
        
        self.api_url = f"http://{ip}:8000"
        self.init_robot()
    
    def init_robot(self):
        try:
            logger.info("client.connecting", url=self.api_url)
            
            self.robot = RemoteRobotController(self.api_url)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.initialize())
            
            self.movement_widget = MovementPanel(self.robot)
            self.led_widget = LEDPanel(self.robot)
            
            self.tabs.insertTab(0, self.movement_widget, "🦿 Movement")
            self.tabs.addTab(self.led_widget, "💡 LEDs")
            self.tabs.setCurrentIndex(0)
            
            self.telemetry_timer = QTimer()
            self.telemetry_timer.timeout.connect(self.update_telemetry)
            self.telemetry_timer.start(1000)
            
            self.status_bar.showMessage(f"✅ Connected to {self.api_url}")
            logger.info("client.ready")
            
        except Exception as e:
            logger.error("client.init_failed", error=str(e))
            QMessageBox.critical(self, "Error", f"Connection failed:\n{e}")
            sys.exit(1)
    
    def update_telemetry(self):
        if not self.robot:
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                battery = loop.run_until_complete(
                    self.robot.sensors.get_battery_voltage()
                )
                self.status_widget.update_battery(battery)
            except:
                pass
            
            try:
                imu = loop.run_until_complete(
                    self.robot.sensors.get_imu_data()
                )
                self.status_widget.update_imu(imu)
            except:
                pass
            
            try:
                distance = loop.run_until_complete(
                    self.robot.sensors.get_distance()
                )
                self.status_widget.update_distance(distance)
            except:
                pass
            
            loop.close()
        except:
            pass
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { background-color: #3c3c3c; color: #ffffff; 
                         border: 1px solid #555; padding: 8px 16px; 
                         border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #4c4c4c; border: 1px solid #0078d4; }
            QTabWidget::pane { border: 1px solid #3c3c3c; }
            QTabBar::tab { background-color: #2b2b2b; color: #ffffff; 
                          padding: 10px 20px; border: 1px solid #3c3c3c; }
            QTabBar::tab:selected { background-color: #3c3c3c; 
                                   border-bottom: 2px solid #0078d4; }
        """)
    
    def keyPressEvent(self, event):
        if hasattr(self, 'movement_widget'):
            self.movement_widget.handle_key_press(event)
    
    def keyReleaseEvent(self, event):
        if hasattr(self, 'movement_widget'):
            self.movement_widget.handle_key_release(event)
    
    def closeEvent(self, event):
        if self.telemetry_timer:
            self.telemetry_timer.stop()
        if self.robot:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.close())
        event.accept()


def signal_handler(sig, frame):
    print("\n🛑 Shutting down client...")
    QApplication.quit()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Allow Ctrl+C
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    
    window = TachikomaClientWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
