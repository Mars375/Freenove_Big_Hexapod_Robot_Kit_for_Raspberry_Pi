# 🤖 TACHIKOMA PROJECT - CONTEXTE COMPLET

## 📋 RÉSUMÉ EXÉCUTIF

**Projet** : Tachikoma - Robot hexapode basé sur Raspberry Pi  
**Date** : 15 Janvier 2026  
**Statut** : Phase 1 COMPLÈTE, Phase 2 en cours (GUI PyQt6)  
**Hardware** : Freenove Big Hexapod Robot Kit pour Raspberry Pi  
**Localisation** : Robot sur 192.168.1.160:8000, PC de développement sur 192.168.1.98

***

## 🎉 DERNIÈRES MISES À JOUR - 15 Janvier 2026

### ✅ **Phase 1 Stabilisée !**

**Bugs récemment fixés** :
1. ✅ **LOC-05/06 : Rotation droite/gauche** - Le paramètre `angle` est maintenant préservé dans le mode `motion`
2. ✅ **LOC-07 : Réglage vitesse** - Confirmé fonctionnel (vitesse 2-10)
3. ✅ **SEN-03 : Sonar distance** - lgpio installé dans le venv, plus de crash

**Résultat** : Locomotion de base **100% stable** !

**Prochaine étape** : **Phase 2 - GUI Desktop PyQt6**

***

## 🏗️ ARCHITECTURE SYSTÈME

### **Stack Technique**
- **Backend** : Python 3.13, FastAPI, Uvicorn
- **Hardware** : Raspberry Pi (modèle 4/5), 18 servomoteurs (PCA9685 dual board)
- **Capteurs** : MPU6050 (IMU), ADS7830 (ADC), HC-SR04 (Ultrason), Caméra
- **Communication** : API REST, WebSocket (en cours), I2C, SPI, GPIO
- **Logging** : Structlog avec format JSON
- **Client** : Terminal Python (asyncio/aiohttp), GUI PyQt6 en développement

### **Structure du Projet**
```
tachikoma/
├── tachikoma/
│   ├── __main__.py              # Point d'entrée
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # Pydantic models
│   │   └── routers/
│   │       ├── movement.py      # Routes locomotion
│   │       ├── leds.py          # Routes LEDs
│   │       ├── sensors.py       # Routes capteurs
│   │       ├── camera.py        # Routes caméra
│   │       └── buzzer.py        # Routes buzzer
│   ├── core/
│   │   ├── robot_controller.py  # Contrôleur principal
│   │   ├── config.py            # Configuration
│   │   └── hardware/
│   │       ├── factory.py       # Factory pattern pour hardware
│   │       ├── movement.py      # Contrôle locomotion
│   │       ├── sensors.py       # Gestion capteurs
│   │       ├── interfaces/
│   │       │   ├── i2c.py       # Interface I2C (SMBus)
│   │       │   └── spi.py       # Interface SPI
│   │       └── drivers/
│   │           ├── pca9685.py   # Driver servos
│   │           ├── mpu6050.py   # Driver IMU
│   │           ├── ultrasonic.py # Driver sonar
│   │           ├── led_strip.py # Driver LEDs (WS2812B)
│   │           └── camera.py    # Driver caméra
│   └── utils/
├── venv/                        # Virtual environment
├── point.txt                    # Fichier calibration servos
└── README.md
```

***

## 🔌 API ENDPOINTS DISPONIBLES

### **Routes Actuelles**
```
📍 HEALTH & DOCS
GET  /                          # Welcome message
GET  /health                    # Health check
GET  /docs                      # Swagger UI
GET  /openapi.json              # OpenAPI schema

🚶 MOVEMENT
POST /api/movement/move         # Commande mouvement
POST /api/movement/attitude     # Ajuster attitude (pitch/roll/yaw)
POST /api/movement/stop         # Arrêt d'urgence
POST /api/movement/test_walk    # Test de marche
GET  /api/movement/calibrate/{leg_id}/{joint}?angle=X  # Calibration servo
POST /api/movement/calibrate/save                      # Sauvegarder calibration

💡 LEDs
POST /api/leds/color            # Couleur fixe RGB
POST /api/leds/brightness       # Luminosité
POST /api/leds/rainbow          # Arc-en-ciel (⚠️ 422 error)
POST /api/leds/off              # Éteindre
GET  /api/leds/status           # État LEDs

📡 SENSORS
GET  /api/sensors/battery       # Voltage batterie
GET  /api/sensors/imu           # Données IMU
GET  /api/sensors/ultrasonic    # Distance sonar
GET  /api/sensors/all           # Tous les capteurs

🎥 CAMERA
POST /api/camera/rotate         # Pan/Tilt caméra
GET  /api/camera/video_feed     # Stream vidéo

🔊 BUZZER
POST /api/buzzer/beep           # Émettre un son

🧠 ADVANCED
GET  /api/advanced/obstacle-avoidance/analyze  # Analyse obstacles
GET  /api/advanced/vision/detect               # Détection objets
GET  /api/advanced/vision/scan-qr              # Scan QR code
```

***

## 📦 MODÈLES DE DONNÉES API

### **MoveCommand**
```python
class MoveCommand(BaseModel):
    mode: str = "motion"           # Mode de mouvement
    x: int = Field(ge=-35, le=35)  # Axe X (-35 à +35)
    y: int = Field(ge=-35, le=35)  # Axe Y (-35 à +35)
    speed: int = Field(ge=2, le=10)  # Vitesse (2 à 10)
    angle: int = Field(ge=-10, le=10)  # Rotation (-10 à +10°)
```

### **AttitudeCommand**
```python
class AttitudeRequest(BaseModel):
    roll: float   # Inclinaison latérale
    pitch: float  # Inclinaison avant/arrière
    yaw: float    # Rotation axe vertical
```

### **LEDColorRequest**
```python
class LEDColorRequest(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
```

***

## ⚙️ CONFIGURATION HARDWARE

### **Servomoteurs**
- **Total** : 18 servos (6 pattes × 3 articulations)
- **Contrôleur** : 2× PCA9685 (I2C addresses 0x40, 0x41)
- **Fréquence** : 50 Hz
- **Pulse range** : 500-2500 µs
- **Layout** :
  - Leg 0-5 : front-right, middle-right, back-right, back-left, middle-left, front-left
  - Joints : coxa (hanche), femur (cuisse), tibia (jambe)

### **Capteurs**
- **IMU** : MPU6050 @ 0x68 (I2C) - Accéléromètre + Gyroscope
- **ADC** : ADS7830 @ 0x48 (I2C) - Batterie dual channel
- **Ultrason** : HC-SR04 - Trigger GPIO 27, Echo GPIO 22
- **Caméra** : Raspberry Pi Camera Module

### **Périphériques**
- **LEDs** : 8× WS2812B - SPI bus 0, device 0
- **Buzzer** : GPIO PWM

***

## 🐛 BUGS IDENTIFIÉS

### **🔴 CRITIQUES**
1. **WebSocket 403 Forbidden**
   - Toutes les tentatives de connexion `/api/v1/ws/ws` rejetées
   - Probablement manque authentification/authorization
   - Orion-SRE essaie de se connecter en boucle

### **🟭 MOYENS**
2. **Rainbow LED 422 Unprocessable**
   - Endpoint existe mais paramètres incorrects
   - Besoin de vérifier le schéma attendu dans `leds.py`

3. **Serveur ne s'arrête plus après crash capteurs**
   - CTRL+C ne fonctionne pas
   - Nécessite `pkill -9`
   - Probablement thread bloqué dans ultrasonic

### **🟭 MINEURS**
4. **Calibration non chargée au démarrage**
   - Warning : `movement.no_calibration_file`
   - Servos utilisent valeurs par défaut

### **✅ RÉCEMMENT FIXÉS (15 Jan 2026)**
- ✅ **Rotation droite/gauche** (LOC-05/06) - Mode `motion` préserve maintenant le paramètre `angle`
- ✅ **Sonar crash** (SEN-03) - `lgpio` installé dans le venv Python
- ✅ **Vitesse** (LOC-07) - Confirmé fonctionnel

***

## ✅ FONCTIONNALITÉS QUI MARCHENT

### **Mouvements**
- ✅ Avancer (y > 0)
- ✅ Reculer (y < 0)
- ✅ Gauche (x < 0)
- ✅ Droite (x > 0)
- ✅ **Rotation droite (angle < 0)** - FIXÉ !
- ✅ **Rotation gauche (angle > 0)** - FIXÉ !
- ✅ Stop
- ✅ Test de marche

### **LEDs**
- ✅ Couleur fixe (1-8)
- ✅ Éteindre
- ⚠️ Rainbow (erreur 422)

### **Capteurs**
- ✅ Batterie (dual channel avec sélection)
- ✅ IMU (pitch/roll/yaw)
- ✅ **Ultrason** - FIXÉ (lgpio installé) !

### **API**
- ✅ FastAPI tourne sur port 8000
- ✅ Swagger docs disponibles
- ✅ Health check
- ✅ CORS configuré

***

## 🎯 ROADMAP COMPLET

### **PHASE 1 - FONDATIONS ✅ COMPLÈTE (15 Jan 2026)**
- [x] Installer lgpio : `sudo apt install python3-lgpio` + `pip install lgpio`
- [x] Fixer rotation : Modifié logique dans `movement.py` ligne 442
- [x] Fixer sonar : lgpio installé dans le venv
- [ ] Fixer rainbow : Vérifier paramètres dans `leds.py`
- [ ] Fixer WebSocket : Ajouter authentification ou désactiver check

### **PHASE 2 - GUI DESKTOP (EN COURS)**
- [ ] **GUI PyQt6 standalone complète**
  - Layout avec onglets (Movement, Camera, LEDs, Sensors, Config, Logs)
  - Joystick virtuel
  - Stream vidéo
  - Graphs temps réel
  - Cross-platform (Windows/Linux/Mac)

### **PHASE 3 - FEATURES CORE**
#### Locomotion avancée
- [ ] Altitude (height offset)
- [ ] Balance (pitch/roll/yaw body)
- [ ] Marche crabe (diagonales)
- [ ] Modes de marche (Tripod, Wave, Ripple)
- [ ] Auto-stabilisation IMU

#### Servos & Calibration
- [ ] Mode Relax (désactivation servos)
- [ ] Auto-calibration
- [ ] Test servos individuels
- [ ] Limites sécurité
- [ ] Trim ajustement

#### Vision & Caméra
- [ ] Stream vidéo HTTP
- [ ] Rotation caméra (Pan/Tilt gauche/droite, haut/bas)
- [ ] Capture photo
- [ ] Enregistrement vidéo

#### LEDs & Audio
- [ ] Gestion complète LEDs (brightness, patterns, animations)
- [ ] Buzzer mélodies
- [ ] Indicateurs d'état

### **PHASE 4 - INTELLIGENCE**
#### Vision avancée
- [ ] Face detection
- [ ] Face recognition + ID
- [ ] Object detection (YOLO)
- [ ] Face tracking
- [ ] Line following
- [ ] QR Code scanning
- [ ] Color blob tracking

#### Navigation autonome
- [ ] Évitement d'obstacles (sonar + vision)
- [ ] Auto-stabilisation
- [ ] Suivi de personne
- [ ] Patrouille automatique
- [ ] Mapping SLAM

### **PHASE 5 - AVANCÉ**
#### IA & Autonomie
- [ ] Modes autonomes (exploration, gardien, jeu)
- [ ] Apprentissage par renforcement
- [ ] Planification de tâches
- [ ] Multi-robot coordination

#### Connectivité
- [ ] WebSocket temps réel
- [ ] MQTT IoT
- [ ] Bluetooth
- [ ] Cloud sync
- [ ] Mobile app

#### Maintenance
- [ ] Auto-diagnostic
- [ ] Alertes proactives
- [ ] OTA updates
- [ ] Backup automatique
- [ ] Recovery mode

***

## 📝 LISTE COMPLÈTE DES FONCTIONNALITÉS

### **🚶 LOCOMOTION (14 features)**
1. ✅ Avancer
2. ✅ Reculer
3. ✅ Aller à droite
4. ✅ Aller à gauche
5. ✅ **Rotation droite** (FIXÉ !)
6. ✅ **Rotation gauche** (FIXÉ !)
7. ✅ **Vitesse 2-10** (Confirmé !)
8. 🔲 Altitude
9. 🔲 Balance
10. 🔲 Marche crabe
11. 🔲 Modes de marche
12. 🔲 Danse
13. 🔲 Auto-stabilisation
14. 🔲 Évitement obstacles

### **🎨 LEDs (10 features)**
1. ✅ Couleur fixe
2. ✅ Éteindre
3. ⚠️ Arc-en-ciel (422)
4. 🔲 Luminosité
5. 🔲 Clignotement
6. 🔲 Respiration
7. 🔲 Vague
8. 🔲 Indicateur batterie
9. 🔲 Indicateur état
10. 🔲 Sync musique

### **🎥 VISION (12 features)**
1. 🔲 Stream vidéo
2. 🔲 Rotation caméra
3. 🔲 Face detection
4. 🔲 Face ID
5. 🔲 Face tracking
6. 🔲 Object detection
7. 🔲 Line following
8. 🔲 QR Code
9. 🔲 Color tracking
10. 🔲 Capture photo
11. 🔲 Recording
12. 🔲 Vision nocturne

### **🔊 AUDIO (7 features)**
1. ✅ Beep simple
2. 🔲 Tonalités
3. 🔲 Mélodies
4. 🔲 Alarmes
5. 🔲 Effets sonores
6. 🔲 Text-to-Speech
7. 🔲 Voice recognition

### **📡 CAPTEURS (11 features)**
1. ✅ Batterie
2. ✅ IMU
3. ✅ **Sonar** (FIXÉ !)
4. 🔲 Gyroscope
5. 🔲 Accéléromètre
6. 🔲 Magnétomètre
7. 🔲 Température
8. 🔲 Pression
9. 🔲 Luminosité
10. 🔲 Courant moteurs
11. 🔲 État servos

### **🎮 CALIBRATION (9 features)**
1. ✅ Calibration manuelle
2. ✅ Sauvegarde calibration
3. 🔲 Auto-calibration
4. 🔲 Relax
5. 🔲 Reset pose
6. 🔲 Test servos
7. 🔲 Diagnostic
8. 🔲 Limites sécurité
9. 🔲 Trim ajustement

### **🤖 MODES AUTONOMES (7 features)**
1. 🔲 Patrouille
2. 🔲 Exploration
3. 🔲 Retour base
4. 🔲 Suivi personne
5. 🔲 Gardien
6. 🔲 Jeu
7. 🔲 Sommeil

### **💾 DONNÉES (6 features)**
1. 🔲 Enregistrement trajectoire
2. 🔲 Replay trajectoire
3. 🔲 Télémétrie
4. 🔲 Logs structurés
5. 🔲 Statistiques
6. 🔲 Black box

### **🌐 CONNECTIVITÉ (6 features)**
1. ✅ API REST
2. ⚠️ WebSocket (403)
3. 🔲 MQTT
4. 🔲 Bluetooth
5. 🔲 WiFi AP
6. 🔲 Cloud sync

### **🖥️ INTERFACES (6 features)**
1. 🔲 GUI Desktop (PyQt6) - EN COURS
2. 🔲 Web Dashboard
3. ✅ Terminal CLI
4. 🔲 Mobile App
5. 🔲 VR/AR Control
6. 🔲 Gamepad support

**TOTAL : 88 fonctionnalités**
- ✅ Fonctionnel : **15 (17%)** ⬆️ +3 depuis hier !
- ⚠️ Partiel/Bugué : 2 (2%)
- 🔲 À développer : 71 (81%)

***

## 🔧 COMMANDES UTILES

### **Sur le Pi (Tachikoma)**
```bash
# Démarrer l'API
cd ~/tachikoma
source venv/bin/activate
python -m tachikoma

# Voir les logs en direct
journalctl -u tachikoma -f

# Tuer serveur crashé
pkill -9 -f "python -m tachikoma"

# Installer lgpio (FIXÉ)
sudo apt install python3-lgpio
pip install lgpio  # Dans le venv !

# Stopper Orion qui spam WebSocket
sudo systemctl stop orion-sre

# Lister les routes API
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/feiyu/tachikoma')
from tachikoma.api.main import app
for route in app.routes:
    if hasattr(route, 'methods'):
        print(f"{list(route.methods)[0]:6s} {route.path}")
EOF
```

### **Sur le PC (Client)**
```bash
# Terminal client
python tachikoma_client_v2.py 192.168.1.160

# Tests API
curl http://192.168.1.160:8000/health
curl http://192.168.1.160:8000/api/sensors/battery
curl -X POST http://192.168.1.160:8000/api/movement/stop

# Tester mouvement
curl -X POST http://192.168.1.160:8000/api/movement/move \
  -H "Content-Type: application/json" \
  -d '{"mode":"motion","x":0,"y":25,"speed":5,"angle":0}'

# Tester rotation (FIXÉ !)
curl -X POST http://192.168.1.160:8000/api/movement/move \
  -H "Content-Type: application/json" \
  -d '{"mode":"motion","x":0,"y":0,"speed":5,"angle":-8}'
```

***

## 📚 RESSOURCES & RÉFÉRENCES

### **Documentation**
- FastAPI : https://fastapi.tiangolo.com/
- Structlog : https://www.structlog.org/
- PyQt6 : https://doc.qt.io/qtforpython-6/
- gpiozero : https://gpiozero.readthedocs.io/

### **Hardware**
- Freenove Kit : https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi
- PCA9685 : https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf
- MPU6050 : https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/

### **Code existant**
- Client terminal : `tachikoma_client_v2.py`
- API router movement : `tachikoma/api/routers/movement.py`
- Hardware factory : `tachikoma/core/hardware/factory.py`

***

## 🎯 PROCHAINES ACTIONS PRIORITAIRES

### **IMMÉDIAT (Aujourd'hui)**
1. ✅ **Fixes Phase 1** - TERMINÉ !
   - ✅ Installer lgpio sur le Pi
   - ✅ Corriger la logique de rotation dans `movement.py`
   - ✅ Tester tous les capteurs

2. **Créer l'interface GUI PyQt6** - EN COURS
   - Layout complet avec onglets
   - Joystick virtuel pour contrôle
   - Intégration vidéo stream
   - Graphs capteurs temps réel

### **COURT TERME (Cette semaine)**
3. **Implémenter les features core manquantes**
   - Mode Relax (désactivation servos)
   - Altitude & Balance
   - Rotation caméra
   - Gestion LEDs complète

### **MOYEN TERME (Ce mois)**
4. **Intelligence & Vision**
   - Face detection
   - Évitement obstacles
   - Modes autonomes

***

## 💡 NOTES IMPORTANTES

### **Contraintes Hardware**
- X, Y limités à **-35 à +35** (pas -1 à 1 !)
- Speed limité à **2 à 10** (pas 0 à 100 !)
- Angle limité à **-10 à +10°**
- 18 servos = 6 pattes × 3 articulations
- Batterie dual channel (sélection du max)

### **Architecture Pattern**
- Factory pattern pour hardware (mock/real)
- Dependency injection via `get_robot_controller()`
- Async/await pour toutes les opérations
- Structured logging avec contexte

***
