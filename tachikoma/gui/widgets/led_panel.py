"""
LED Panel - LED color and effects control
RGB color presets + animated effects
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QSlider, QLabel, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from tachikoma.core.robot_controller import RobotController
from tachikoma.core.logger import get_logger

logger = get_logger(__name__)


class LEDPanel(QWidget):
    """LED control panel with colors and effects."""
    
    def __init__(self, robot: RobotController):
        super().__init__()
        self.robot = robot
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Color presets
        presets_group = QGroupBox("🎨 Color Presets")
        presets_layout = QGridLayout()
        
        colors = [
            ("🔴 Red", (255, 0, 0), "#ff0000"),
            ("🟢 Green", (0, 255, 0), "#00ff00"),
            ("🔵 Blue", (0, 0, 255), "#0000ff"),
            ("🟡 Yellow", (255, 255, 0), "#ffff00"),
            ("🟣 Purple", (255, 0, 255), "#ff00ff"),
            ("🔵 Cyan", (0, 255, 255), "#00ffff"),
            ("🟠 Orange", (255, 165, 0), "#ffa500"),
            ("⚪ White", (255, 255, 255), "#ffffff"),
            ("🟤 Pink", (255, 192, 203), "#ffc0cb"),
            ("⚫ Off", (0, 0, 0), "#000000"),
        ]
        
        row, col = 0, 0
        for name, rgb, hex_color in colors:
            btn = QPushButton(name)
            btn.setMinimumSize(140, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_color};
                    color: {'#000000' if hex_color in ['#ffff00', '#ffffff', '#ffc0cb', '#ffa500'] else '#ffffff'};
                    font-weight: bold;
                    font-size: 13px;
                    border: 2px solid #555555;
                }}
                QPushButton:hover {{
                    border: 2px solid #0078d4;
                }}
            """)
            btn.clicked.connect(lambda checked, r=rgb: self.set_color(*r))
            presets_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        # Custom RGB sliders
        custom_group = QGroupBox("🎛️ Custom RGB Color")
        custom_layout = QVBoxLayout()
        
        # Red slider
        red_layout = QHBoxLayout()
        red_layout.addWidget(QLabel("R:"))
        self.red_slider = QSlider(Qt.Orientation.Horizontal)
        self.red_slider.setMinimum(0)
        self.red_slider.setMaximum(255)
        self.red_slider.setValue(0)
        red_layout.addWidget(self.red_slider)
        self.red_label = QLabel("0")
        self.red_label.setMinimumWidth(40)
        self.red_label.setStyleSheet("font-weight: bold;")
        self.red_slider.valueChanged.connect(
            lambda v: self.red_label.setText(str(v))
        )
        red_layout.addWidget(self.red_label)
        custom_layout.addLayout(red_layout)
        
        # Green slider
        green_layout = QHBoxLayout()
        green_layout.addWidget(QLabel("G:"))
        self.green_slider = QSlider(Qt.Orientation.Horizontal)
        self.green_slider.setMinimum(0)
        self.green_slider.setMaximum(255)
        self.green_slider.setValue(0)
        green_layout.addWidget(self.green_slider)
        self.green_label = QLabel("0")
        self.green_label.setMinimumWidth(40)
        self.green_label.setStyleSheet("font-weight: bold;")
        self.green_slider.valueChanged.connect(
            lambda v: self.green_label.setText(str(v))
        )
        green_layout.addWidget(self.green_label)
        custom_layout.addLayout(green_layout)
        
        # Blue slider
        blue_layout = QHBoxLayout()
        blue_layout.addWidget(QLabel("B:"))
        self.blue_slider = QSlider(Qt.Orientation.Horizontal)
        self.blue_slider.setMinimum(0)
        self.blue_slider.setMaximum(255)
        self.blue_slider.setValue(0)
        blue_layout.addWidget(self.blue_slider)
        self.blue_label = QLabel("0")
        self.blue_label.setMinimumWidth(40)
        self.blue_label.setStyleSheet("font-weight: bold;")
        self.blue_slider.valueChanged.connect(
            lambda v: self.blue_label.setText(str(v))
        )
        blue_layout.addWidget(self.blue_label)
        custom_layout.addLayout(blue_layout)
        
        # Preview and apply
        preview_layout = QHBoxLayout()
        self.color_preview = QLabel()
        self.color_preview.setMinimumSize(100, 50)
        self.color_preview.setStyleSheet("border: 2px solid #555555; background-color: #000000;")
        preview_layout.addWidget(self.color_preview)
        
        btn_apply_custom = QPushButton("✅ Apply Custom Color")
        btn_apply_custom.setMinimumHeight(50)
        btn_apply_custom.clicked.connect(self.apply_custom_color)
        preview_layout.addWidget(btn_apply_custom)
        custom_layout.addLayout(preview_layout)
        
        # Connect sliders to preview
        self.red_slider.valueChanged.connect(self.update_preview)
        self.green_slider.valueChanged.connect(self.update_preview)
        self.blue_slider.valueChanged.connect(self.update_preview)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # Effects
        effects_group = QGroupBox("✨ Animated Effects")
        effects_layout = QGridLayout()
        
        effects = [
            ("🌈 Rainbow", self.effect_rainbow),
            ("💫 Breathe", self.effect_breathe),
            ("⚡ Strobe", self.effect_strobe),
            ("🌊 Wave", self.effect_wave),
            ("🔥 Fire", self.effect_fire),
            ("❄️ Ice", self.effect_ice),
        ]
        
        row, col = 0, 0
        for name, callback in effects:
            btn = QPushButton(name)
            btn.setMinimumSize(140, 50)
            btn.clicked.connect(callback)
            effects_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_preview(self):
        """Update color preview."""
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        
        self.color_preview.setStyleSheet(
            f"border: 2px solid #555555; background-color: rgb({r}, {g}, {b});"
        )
    
    def set_color(self, r: int, g: int, b: int):
        """Set LED color."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.leds.set_color(r, g, b))
            logger.info("gui.led.color_set", r=r, g=g, b=b)
        except Exception as e:
            logger.error("gui.led.set_color_failed", error=str(e))
    
    def apply_custom_color(self):
        """Apply custom RGB color."""
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        self.set_color(r, g, b)
    
    def effect_rainbow(self):
        """Rainbow effect."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.leds.rainbow())
            logger.info("gui.led.effect", effect="rainbow")
        except Exception as e:
            logger.error("gui.led.effect_failed", effect="rainbow", error=str(e))
    
    def effect_breathe(self):
        """Breathing effect."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.leds.breathe())
            logger.info("gui.led.effect", effect="breathe")
        except Exception as e:
            logger.error("gui.led.effect_failed", effect="breathe", error=str(e))
    
    def effect_strobe(self):
        """Strobe effect."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.leds.strobe())
            logger.info("gui.led.effect", effect="strobe")
        except Exception as e:
            logger.error("gui.led.effect_failed", effect="strobe", error=str(e))
    
    def effect_wave(self):
        """Wave effect."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Implement wave effect if exists, otherwise fallback
            loop.run_until_complete(self.robot.leds.set_color(0, 100, 255))
            logger.info("gui.led.effect", effect="wave")
        except Exception as e:
            logger.error("gui.led.effect_failed", effect="wave", error=str(e))
    
    def effect_fire(self):
        """Fire effect."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.leds.set_color(255, 50, 0))
            logger.info("gui.led.effect", effect="fire")
        except Exception as e:
            logger.error("gui.led.effect_failed", effect="fire", error=str(e))
    
    def effect_ice(self):
        """Ice effect."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.leds.set_color(150, 200, 255))
            logger.info("gui.led.effect", effect="ice")
        except Exception as e:
            logger.error("gui.led.effect_failed", effect="ice", error=str(e))
