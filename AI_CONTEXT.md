# 🤖 TACHIKOMA PROJECT - CONTEXTE ULTRA-DÉTAILLÉ

## 📋 MÉTA-INFORMATIONS

**Nom du projet** : Tachikoma  
**Inspiration** : Référence à Ghost in the Shell (tanks autonomes multi-pattes)  
**Date de création** : ~2025  
**Date actuelle** : 15 Janvier 2026, 09:51 CET  
**Développeur principal** : Développeur frontend & PsyOps basé à Châteauneuf-sur-Cher, France  
**Statut emploi** : Actuellement au chômage, monte son propre SRE  
**Compétences** : Frontend, Python backend, Systems engineering, Infrastructure (Orion-SRE)  
**Hobbies** : Échecs, Badminton, Hardware/Robotique  

***

## 🌐 ÉCOSYSTÈME & CONTEXTE PERSONNEL

### **Projets Connexes**
- **Orion-SRE** : Système de Site Reliability Engineering personnel développé sur Raspberry Pi
  - Modules : Guardian, Brain, Healer, Commander, Narrator
  - Architecture événementielle avec message bus
  - Monitoring et healing automatique
  - Actuellement en conflit avec Tachikoma (spam WebSocket)

### **Infrastructure Actuelle**
- **Hôte principal** : `JARVIS` (nom de machine Ghost in the Shell)
- **Utilisateur** : `orion` (précédemment `feiyu`)
- **Réseau local** :
  - Tachikoma (Raspberry Pi) : `192.168.1.160:8000`
  - PC développement : `192.168.1.98`
  - Gateway probablement : `192.168.1.1`

### **Setup Développement**
- **OS Pi** : Raspberry Pi OS (Debian-based)
- **Python** : 3.12 (venv montre python3.12)
- **IDE/Éditeur** : Probablement VS Code ou terminal-based
- **Workflow** : SSH pour développement distant, Git pour versionning

***

## 🏗️ ARCHITECTURE DÉTAILLÉE

### **Structure Actuelle (Post-Migration)**

```
~/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/  ← ⚠️ NOM BANCAL
├── 📄 Makefile                    # Commandes utiles (make run, make test, etc.)
├── 📄 pyproject.toml              # Config Python moderne
├── 📄 requirements.txt            # Dépendances
├── 📄 .env.example                # Template variables environnement
├── 📄 .gitignore                  # Exclusions Git
│
├── 📁 data/                       # Données configuration
│   ├── config.yaml                # Config générale
│   ├── logging.yaml               # Config logs structlog
│   └── params.json                # Paramètres hardware
│
├── 📁 logs/                       # Logs applicatifs (vide actuellement)
│
├── 📄 point.txt -> data/point.txt # Symlink calibration servos
│
├── 📁 scripts/                    # Scripts utilitaires standalone
│   ├── test_camera.py
│   ├── test_hardware.py
│   ├── test_servos.py
│   ├── test_ultrasonic.py
│   └── test_walk.py
│
├── 📁 docs/                       # Documentation externe
│   └── hardware/
│       └── servo_mapping.md
│
├── 📁 tests/                      # Tests unitaires et intégration
│   ├── conftest.py                # Config pytest
│   ├── unit/                      # Tests unitaires
│   │   ├── test_config.py
│   │   ├── test_robot_controller.py
│   │   ├── test_pca9685_servo.py
│   │   ├── test_imu.py
│   │   ├── test_adc.py
│   │   ├── test_ultrasonic.py
│   │   ├── test_led_driver.py
│   │   ├── test_buzzer.py
│   │   ├── test_mock_servo.py
│   │   ├── test_obstacle_avoidance.py
│   │   └── test_vision.py
│   └── integration/               # Tests d'intégration
│       ├── test_api.py
│       ├── test_hardware_factory.py
│       ├── test_movement_api.py
│       ├── test_leds_api.py
│       ├── test_sensors_api.py
│       ├── test_camera_api.py
│       ├── test_buzzer_api.py
│       └── test_websocket_api.py
│
├── 📁 venv/                       # Virtual environment Python
│   ├── bin/                       # Exécutables (python, pip, uvicorn, etc.)
│   ├── lib/python3.12/site-packages/
│   └── pyvenv.cfg
│
├── 📄 tachikoma_client_final.py   # ⚠️ CLIENT À LA RACINE (bancal)
│
└── 📁 tachikoma/                  # ⭐ MODULE PRINCIPAL
    ├── 📄 README.md               # ⚠️ Doc dans module (bancal)
    ├── 📄 CONTEXT.md              # ⚠️ Doc dans module (bancal)
    ├── 📄 ROADMAP.md              # ⚠️ Doc dans module (bancal)
    ├── 📄 ADR.md                  # ⚠️ Architecture Decision Records dans module
    ├── 📄 FREENOVE_ANALYSIS.md    # ⚠️ Analyse dans module (bancal)
    ├── 📄 __init__.py
    ├── 📄 __main__.py             # Point d'entrée: python -m tachikoma
    │
    ├── 📁 api/                    # API REST FastAPI
    │   ├── __init__.py
    │   ├── main.py                # App FastAPI principale
    │   ├── models.py              # Modèles Pydantic
    │   └── routers/               # Routes par domaine
    │       ├── __init__.py
    │       ├── movement.py        # Locomotion
    │       ├── leds.py            # LEDs
    │       ├── sensors.py         # Capteurs
    │       ├── camera.py          # Caméra
    │       ├── buzzer.py          # Buzzer
    │       ├── advanced.py        # Features avancées (vision, auto)
    │       └── websocket.py       # WebSocket temps réel
    │
    ├── 📁 core/                   # Logique métier core
    │   ├── __init__.py
    │   ├── config.py              # Configuration chargée depuis data/
    │   ├── logger.py              # Setup structlog
    │   ├── exceptions.py          # Exceptions custom
    │   ├── dependencies.py        # Dependency injection FastAPI
    │   ├── robot_controller.py    # Contrôleur principal robot
    │   └── hardware/              # Abstraction hardware
    │       ├── __init__.py
    │       ├── factory.py         # Factory pattern (mock/real)
    │       ├── movement.py        # Contrôle locomotion
    │       ├── sensors.py         # Gestion capteurs
    │       ├── leds.py            # Contrôle LEDs
    │       ├── buzzer.py          # Contrôle buzzer
    │       ├── camera.py          # Contrôle caméra
    │       ├── kinematics.py      # Cinématique inverse
    │       ├── gaits.py           # Algorithmes de marche
    │       ├── interfaces/        # Interfaces bus hardware
    │       │   ├── __init__.py
    │       │   ├── i2c.py         # Interface I2C (SMBus)
    │       │   └── spi.py         # Interface SPI
    │       ├── drivers/           # Drivers bas niveau
    │       │   ├── __init__.py
    │       │   ├── pca9685.py     # Driver contrôleur servos
    │       │   ├── mpu6050.py     # Driver IMU
    │       │   ├── ads7830.py     # Driver ADC (batterie)
    │       │   ├── ultrasonic.py  # Driver sonar
    │       │   ├── led_strip.py   # Driver WS2812B
    │       │   └── camera_driver.py
    │       ├── controllers/       # Contrôleurs de haut niveau
    │       │   └── servo_controller.py
    │       └── devices/           # Abstractions devices
    │           └── servo.py
    │
    ├── 📁 features/               # Features avancées
    │   ├── __init__.py
    │   ├── autonomous/            # Navigation autonome
    │   │   ├── __init__.py
    │   │   └── obstacle_avoidance.py
    │   ├── vision/                # Vision par ordinateur
    │   │   ├── __init__.py
    │   │   ├── object_detection.py
    │   │   └── qr_scanner.py
    │   ├── telemetry/             # Télémétrie et métriques
    │   │   └── __init__.py
    │   └── orion_bridge/          # Intégration Orion-SRE
    │       └── __init__.py
    │
    ├── 📁 cli/                    # Interface ligne de commande
    │   └── __init__.py
    │
    └── 📁 gui/                    # Interface graphique PyQt6
        ├── __init__.py
        ├── client.py              # Application principale
        └── widgets/               # Composants GUI
            ├── __init__.py
            ├── movement_panel.py
            ├── camera_panel.py
            ├── led_panel.py
            ├── status_panel.py
            └── calibration_panel.py
```

***

## 🚨 PROBLÈMES STRUCTURELS IDENTIFIÉS

### **❌ BANCALITÉS POST-MIGRATION**

1. **📂 Nom du dossier racine**
   - Actuel : `Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi`
   - Problème : Long, pas professionnel, référence kit d'origine
   - Solution : Renommer en `tachikoma-robot` ou `tachikoma`

2. **📄 Documentation mal placée**
   - `tachikoma/README.md` → devrait être à la racine
   - `tachikoma/CONTEXT.md` → devrait être dans `docs/`
   - `tachikoma/ROADMAP.md` → devrait être à la racine ou `docs/`
   - `tachikoma/ADR.md` → devrait être dans `docs/architecture/`
   - `tachikoma/FREENOVE_ANALYSIS.md` → devrait être dans `docs/`

3. **🐍 Client mal placé**
   - `tachikoma_client_final.py` à la racine
   - Solution : Déplacer dans `scripts/` ou intégrer dans `tachikoma/cli/`

4. **🔄 Structure redondante**
   - `tachikoma/` contient le code ET de la doc
   - Confusion entre module Python et racine projet

5. **📦 Gestion dépendances mixte**
   - `requirements.txt` ET `pyproject.toml`
   - Solution : Choisir un seul (pyproject.toml moderne préféré)

***

## 🔧 STRUCTURE PROPOSÉE (CLEAN)

```
~/tachikoma-robot/                 # ✅ Nom clean et professionnel
├── 📄 README.md                   # ✅ Doc principale à la racine
├── 📄 ROADMAP.md                  # ✅ Roadmap à la racine
├── 📄 pyproject.toml              # ✅ Config unique moderne
├── 📄 Makefile
├── 📄 .env.example
├── 📄 .gitignore
│
├── 📁 docs/                       # ✅ Toute la doc centralisée
│   ├── CONTEXT.md                 # Déplacé depuis tachikoma/
│   ├── FREENOVE_ANALYSIS.md       # Déplacé depuis tachikoma/
│   ├── architecture/
│   │   └── ADR.md                 # Déplacé depuis tachikoma/
│   ├── hardware/
│   │   └── servo_mapping.md
│   ├── api/
│   │   └── endpoints.md           # Documentation API
│   └── guides/
│       ├── installation.md
│       ├── calibration.md
│       └── troubleshooting.md
│
├── 📁 config/                     # ✅ Renommé depuis data/
│   ├── config.yaml
│   ├── logging.yaml
│   ├── params.json
│   └── point.txt                  # Fichier calibration (pas de symlink)
│
├── 📁 logs/                       # Logs runtime
│
├── 📁 scripts/                    # Scripts utilitaires
│   ├── test_camera.py
│   ├── test_hardware.py
│   ├── test_servos.py
│   ├── test_ultrasonic.py
│   ├── test_walk.py
│   └── client.py                  # ✅ Client déplacé ici
│
├── 📁 tests/                      # Tests
│   ├── conftest.py
│   ├── unit/
│   └── integration/
│
├── 📁 venv/                       # Virtual environment
│
└── 📁 tachikoma/                  # ✅ MODULE PURE (sans docs)
    ├── __init__.py
    ├── __main__.py
    ├── api/
    ├── core/
    ├── features/
    ├── cli/
    └── gui/
```

***

## 📦 DÉPENDANCES COMPLÈTES

### **requirements.txt Actuel**
```txt
# FastAPI & Web
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
websockets>=14.1
python-dotenv>=1.0.0

# Hardware
smbus2>=0.4.3
spidev>=3.6
gpiozero>=2.0.0
RPi.GPIO>=0.7.1
adafruit-circuitpython-pca9685>=3.4.0
adafruit-circuitpython-servokit>=1.3.12
lgpio>=0.2.2.0              # ⚠️ CRITIQUE pour Python 3.13+

# Vision & AI
opencv-python>=4.10.0
numpy>=1.26.0
pillow>=10.0.0
pyzbar>=0.1.9               # QR code scanning

# Logging & Monitoring
structlog>=24.4.0

# GUI (PyQt6)
PyQt6>=6.7.0
PyQt6-WebEngine>=6.7.0

# Utils
pyyaml>=6.0
pyserial>=3.5

# Dev & Testing
pytest>=8.3.0
pytest-asyncio>=0.24.0
black>=24.8.0
ruff>=0.6.0
mypy>=1.11.0
```

### **pyproject.toml Actuel**
```toml
[project]
name = "tachikoma"
version = "2.0.0"
description = "Advanced Hexapod Robot Control System"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "structlog>=24.4.0",
    "smbus2>=0.4.3",
    "gpiozero>=2.0.0",
    # ... etc
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "black>=24.8.0",
    "ruff>=0.6.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I"]
```

***

## 🔌 API ENDPOINTS - DÉTAIL COMPLET

### **Format de Réponse Standard**
```json
{
  "success": true/false,
  "message": "Description",
  "data": {},           // Optionnel
  "command": "CMD_XXX"  // Optionnel pour debug
}
```

### **Routes Health**
```
GET  /                 → {"message": "Tachikoma API v2.0.0"}
GET  /health           → {"status": "ok", "version": "2.0.0"}
GET  /docs             → Swagger UI interactif
GET  /redoc            → ReDoc alternative
GET  /openapi.json     → Spécification OpenAPI 3.0
```

### **Routes Movement** (`/api/movement/`)

#### `POST /api/movement/move`
**Request Body:**
```json
{
  "mode": "motion",      // string
  "x": 0,                // int (-35 à 35)
  "y": 25,               // int (-35 à 35)
  "speed": 5,            // int (2 à 10)
  "angle": 0             // int (-10 à 10)
}
```
**Response:**
```json
{
  "success": true,
  "message": "Movement command sent successfully",
  "command": "CMD_MOVE#motion#0#25#5#0"
}
```

#### `POST /api/movement/attitude`
**Request Body:**
```json
{
  "roll": 0.0,   // float (degrés)
  "pitch": 0.0,  // float (degrés)
  "yaw": 0.0     // float (degrés)
}
```

#### `POST /api/movement/stop`
**Response:**
```json
{
  "success": true,
  "message": "Robot stopped successfully"
}
```

#### `POST /api/movement/test_walk?speed=5&duration=3.0`
**Query Params:**
- `speed` : int (défaut 5)
- `duration` : float (défaut 5.0 secondes)

#### `GET /api/movement/calibrate/{leg_id}/{joint}?angle=90`
**Path Params:**
- `leg_id` : 0-5 (front-right, middle-right, back-right, back-left, middle-left, front-left)
- `joint` : "coxa" | "femur" | "tibia"
**Query Param:**
- `angle` : 0-180

**Response:**
```json
{
  "leg": 0,
  "joint": "coxa",
  "angle": 90,
  "servo_channel": 0
}
```

#### `POST /api/movement/calibrate/save`
**Request Body:**
```json
{
  "0": {"coxa": 90, "femur": 90, "tibia": 90},
  "1": {"coxa": 90, "femur": 90, "tibia": 90},
  ...
  "5": {"coxa": 90, "femur": 90, "tibia": 90}
}
```

### **Routes LEDs** (`/api/leds/`)

#### `POST /api/leds/color`
```json
{
  "r": 255,  // 0-255
  "g": 0,    // 0-255
  "b": 0     // 0-255
}
```

#### `POST /api/leds/brightness`
```json
{
  "brightness": 128  // 0-255
}
```

#### `POST /api/leds/rainbow`
⚠️ Actuellement 422 - Paramètres à vérifier

#### `POST /api/leds/off`
Pas de body

#### `GET /api/leds/status`
**Response:**
```json
{
  "enabled": true,
  "current_color": [255, 0, 0],
  "brightness": 255,
  "mode": "static"
}
```

### **Routes Sensors** (`/api/sensors/`)

#### `GET /api/sensors/battery`
```json
{
  "voltage": 7.58,  // Volts
  "battery1": 6.47,
  "battery2": 7.58,
  "selected": "battery2"
}
```

#### `GET /api/sensors/imu`
```json
{
  "pitch": 2.3,   // degrés
  "roll": -1.1,   // degrés
  "yaw": 45.0,    // degrés
  "accel_x": 0.1,
  "accel_y": 0.0,
  "accel_z": 9.8,
  "gyro_x": 0.0,
  "gyro_y": 0.0,
  "gyro_z": 0.0
}
```

#### `GET /api/sensors/ultrasonic`
⚠️ Crash si lgpio non installé
```json
{
  "distance": 23.5  // centimètres
}
```

#### `GET /api/sensors/all`
⚠️ Peut crasher à cause de ultrasonic
```json
{
  "battery": {...},
  "imu": {...},
  "ultrasonic": {...}
}
```

### **Routes Camera** (`/api/camera/`)

#### `POST /api/camera/rotate`
```json
{
  "pan": 0,   // -90 à 90 (gauche/droite)
  "tilt": 0   // -90 à 90 (haut/bas)
}
```

#### `GET /api/camera/video_feed`
Retourne un stream MJPEG

### **Routes Buzzer** (`/api/buzzer/`)

#### `POST /api/buzzer/beep`
```json
{
  "frequency": 1000,  // Hz
  "duration": 0.5     // secondes
}
```

### **Routes Advanced** (`/api/advanced/`)

#### `GET /api/advanced/obstacle-avoidance/analyze`
```json
{
  "obstacles_detected": true,
  "distance_front": 23.5,
  "recommended_action": "turn_left",
  "confidence": 0.85
}
```

#### `GET /api/advanced/vision/detect`
```json
{
  "objects": [
    {"class": "person", "confidence": 0.92, "bbox": [x, y, w, h]},
    {"class": "chair", "confidence": 0.78, "bbox": [x, y, w, h]}
  ]
}
```

#### `GET /api/advanced/vision/scan-qr`
```json
{
  "qr_detected": true,
  "data": "https://example.com",
  "type": "QR_CODE"
}
```

### **Routes WebSocket** (`/api/v1/ws/`)

#### `WS /api/v1/ws/ws`
⚠️ Actuellement 403 Forbidden
Format messages:
```json
{
  "type": "telemetry",
  "data": {
    "battery": 7.58,
    "imu": {...},
    "position": {...}
  },
  "timestamp": "2026-01-15T09:51:00Z"
}
```

***

## 🔩 HARDWARE DÉTAILLÉ

### **Raspberry Pi Configuration**
- **Modèle** : Probablement Pi 4 ou 5 (basé sur lgpio requirement)
- **RAM** : Minimum 2GB (recommandé 4GB)
- **OS** : Raspberry Pi OS Bookworm (Debian 12-based)
- **Python** : 3.12 (venv montre 3.12, mais doc mentionne 3.13 parfois)
- **Hostname** : `tachikoma` ou similaire
- **IP** : 192.168.1.160

### **Pinout GPIO**
```
Ultrasonic:
  - Trigger: GPIO 27
  - Echo: GPIO 22

Buzzer:
  - Pin: GPIO (à documenter)

Camera:
  - CSI port (ribbon cable)

Servo PAN/TILT Camera:
  - PCA9685 channels (à documenter)
```

### **Bus I2C (Bus 1 par défaut)**
```
0x40 - PCA9685 Board 1 (Servos 0-15)
0x41 - PCA9685 Board 2 (Servos 16-17 + camera servos)
0x48 - ADS7830 ADC (Battery monitoring)
0x68 - MPU6050 IMU (Accelerometer + Gyroscope)
```

### **Bus SPI**
```
SPI0 (Bus 0, Device 0):
  - WS2812B LED Strip (8 LEDs)
  - MOSI: GPIO 10
  - SCLK: GPIO 11
  - CE0: GPIO 8
```

### **Servomoteurs Mapping**
```
Leg 0 (Front Right):
  - Servo 0: Coxa (hanche)
  - Servo 1: Femur (cuisse)
  - Servo 2: Tibia (jambe)

Leg 1 (Middle Right):
  - Servo 3: Coxa
  - Servo 4: Femur
  - Servo 5: Tibia

Leg 2 (Back Right):
  - Servo 6: Coxa
  - Servo 7: Femur
  - Servo 8: Tibia

Leg 3 (Back Left):
  - Servo 9: Coxa
  - Servo 10: Femur
  - Servo 11: Tibia

Leg 4 (Middle Left):
  - Servo 12: Coxa
  - Servo 13: Femur
  - Servo 14: Tibia

Leg 5 (Front Left):
  - Servo 15: Coxa
  - Servo 16: Femur
  - Servo 17: Tibia

Camera (optionnel):
  - Servo 18 ou 19: Pan (gauche/droite)
  - Servo 19 ou 20: Tilt (haut/bas)
```

### **Calibration Format (point.txt)**
```
90,90,90    # Leg 0: coxa,femur,tibia
90,90,90    # Leg 1
90,90,90    # Leg 2
90,90,90    # Leg 3
90,90,90    # Leg 4
90,90,90    # Leg 5
```

### **Batterie**
- Type: Dual battery pack
- Monitoring: ADS7830 ADC dual channel
- Voltage nominal: ~7.4V (2S LiPo)
- Seuil bas: ~6.0V
- Seuil critique: <5.5V

***

## 🐛 BUGS - DIAGNOSTIC COMPLET

### **🔴 BUG #1: Rotation ne fonctionne pas**

**Symptômes:**
```python
await robot.movement.move(mode="motion", x=0, y=0, speed=5, angle=-8)
# Résultat: Robot s'arrête au lieu de tourner
```

**Logs:**
```
movement.move.zero_params.stopping
```

**Cause Root:**
Dans `tachikoma/core/hardware/movement.py`, la logique détecte si `x == 0 AND y == 0` et considère ça comme "pas de mouvement", ignorant `angle`.

**Code Problématique:**
```python
def move(self, x, y, speed, angle):
    if x == 0 and y == 0:  # ❌ BUG: Ignore angle!
        self.stop()
        return
    # ...
```

**Fix:**
```python
def move(self, x, y, speed, angle):
    if x == 0 and y == 0 and angle == 0:  # ✅ Check angle aussi
        self.stop()
        return
    # ...
```

**Workaround Temporaire:**
```python
# Au lieu de:
move(x=0, y=0, angle=-8)
# Utiliser:
move(x=0, y=1, angle=-8)  # y=1 force le mouvement
```

***

### **🔴 BUG #2: Sonar crash avec lgpio**

**Symptômes:**
```
ultrasonic.gpio_issue error='Failed to add edge detection'
PWMSoftwareFallback: For more accurate readings, use the pigpio pin factory
DistanceSensorNoEcho: no echo received
```

**Cause Root:**
Python 3.13+ sur Raspberry Pi 4/5 requiert `lgpio` pour `gpiozero`, mais pas installé.

**Fix:**
```bash
sudo apt update
sudo apt install -y python3-lgpio
# OU dans venv:
pip install lgpio
```

**Vérification:**
```python
import gpiozero
print(gpiozero.Device.pin_factory)
# Doit afficher: <lgpio.LGPIOFactory object>
```

***

### **🔴 BUG #3: WebSocket 403 Forbidden**

**Symptômes:**
```
INFO: 192.168.1.98:63621 - "WebSocket /api/v1/ws/ws" 403
INFO: connection rejected (403 Forbidden)
```

**Cause Probable:**
Middleware d'authentification ou CORS bloque les connexions WebSocket.

**Code à Vérifier:**
`tachikoma/api/routers/websocket.py`

**Fix Potentiel:**
```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # ❌ Manque peut-être:
    await websocket.accept()
    # ...
```

**OU** Dans `main.py`:
```python
# S'assurer que CORS autorise WebSocket
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

***

### **🟡 BUG #4: Rainbow LED 422**

**Symptômes:**
```
POST /api/leds/rainbow HTTP/1.1" 422 Unprocessable Content
```

**Cause:**
Paramètres manquants ou incorrects dans la requête.

**À Vérifier:**
```bash
cat ~/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/tachikoma/api/routers/leds.py | grep -A 20 "rainbow"
```

**Fix Potentiel:**
Ajouter des paramètres optionnels:
```python
@router.post("/rainbow")
async def rainbow_mode(
    speed: float = 1.0,      # Vitesse animation
    duration: float = 10.0   # Durée
):
    # ...
```

***

### **🟡 BUG #5: Serveur ne s'arrête plus**

**Symptômes:**
CTRL+C ne fonctionne pas après erreur ultrasonic, nécessite `pkill -9`.

**Cause:**
Thread bloqué dans `gpiozero.DistanceSensor` en attente d'echo.

**Fix:**
Ajouter timeout dans ultrasonic driver:
```python
class UltrasonicSensor:
    def measure_distance(self):
        try:
            with Timeout(seconds=2):  # ✅ Timeout 2s
                distance = self.sensor.distance
                return distance * 100
        except TimeoutError:
            logger.warning("ultrasonic.timeout")
            return None
```

***

### **🟢 BUG #6: Orion-SRE spam WebSocket**

**Symptômes:**
Logs montrent tentatives répétées de connexion WebSocket depuis Orion.

**Solution:**
```bash
# Sur le Pi
sudo systemctl stop orion-sre
# OU désactiver au boot:
sudo systemctl disable orion-sre
```

**OU** Configurer Orion pour ne pas essayer de se connecter à Tachikoma:
```yaml
# Orion config
connectors:
  tachikoma:
    enabled: false
```

***

## 📊 MÉTRIQUES & MONITORING

### **Logs Structurés (structlog)**
```python
logger.info(
    "movement.move",
    mode="motion",
    x=0,
    y=25,
    speed=5,
    angle=0,
    robot="Hexapod-01",
    version="2.0.0"
)
```

**Format JSON:**
```json
{
  "event": "movement.move",
  "mode": "motion",
  "x": 0,
  "y": 25,
  "speed": 5,
  "angle": 0,
  "robot": "Hexapod-01",
  "version": "2.0.0",
  "timestamp": "2026-01-15T09:51:23.456789Z",
  "level": "info"
}
```

### **Métriques à Exposer (Futur)**
- Uptime
- Battery voltage (temps réel)
- Distance parcourue
- Nombre de mouvements
- Erreurs hardware
- Latence API
- FPS caméra

***

## 🎯 PLAN DE REFACTORING

### **Phase 1: Restructuration (Aujourd'hui)**

```bash
cd ~
mv Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi tachikoma-robot
cd tachikoma-robot

# Réorganiser docs
mkdir -p docs/architecture
mv tachikoma/README.md README.md
mv tachikoma/ROADMAP.md ROADMAP.md
mv tachikoma/CONTEXT.md docs/CONTEXT.md
mv tachikoma/ADR.md docs/architecture/ADR.md
mv tachikoma/FREENOVE_ANALYSIS.md docs/FREENOVE_ANALYSIS.md

# Réorganiser config
mkdir -p config
mv data/* config/
rm data  # supprimer vieux dossier
rm point.txt  # supprimer symlink
mv config/point.txt config/point.txt  # direct

# Réorganiser client
mv tachikoma_client_final.py scripts/client.py

# Commit
git add .
git commit -m "refactor: clean project structure"
```

### **Phase 2: Fix Bugs (Aujourd'hui)**

1. **Installer lgpio:**
```bash
sudo apt install -y python3-lgpio
```

2. **Fixer rotation dans movement.py:**
```python
# Dans tachikoma/core/hardware/movement.py
def move(self, ...):
    # Ligne ~150-160
    if x == 0 and y == 0 and angle == 0:  # ✅ Ajout check angle
        await self.stop()
        return
```

3. **Fixer rainbow endpoint:**
```bash
# Vérifier paramètres attendus
cat tachikoma/api/routers/leds.py | grep -A 30 "rainbow"
# Ajuster selon schéma trouvé
```

4. **Stopper Orion:**
```bash
sudo systemctl stop orion-sre
```

### **Phase 3: GUI Standalone (Cette semaine)**

Créer `tachikoma/gui/main.py` avec PyQt6:
- Onglets: Movement, Camera, LEDs, Sensors, Config, Logs
- Joystick virtuel
- Stream vidéo
- Graphs temps réel

### **Phase 4: Features Core (Ce mois)**

- Mode Relax
- Altitude & Balance
- Rotation caméra
- Gestion LEDs complète
- Face detection

***

## 🚀 COMMANDES MAKE DISPONIBLES

```makefile
# Makefile contenu probable:
run:
    python -m tachikoma

test:
    pytest tests/

test-unit:
    pytest tests/unit/

test-integration:
    pytest tests/integration/

lint:
    ruff check tachikoma/
    black --check tachikoma/

format:
    black tachikoma/
    ruff check --fix tachikoma/

clean:
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

install:
    pip install -e .

install-dev:
    pip install -e ".[dev]"
```

***
