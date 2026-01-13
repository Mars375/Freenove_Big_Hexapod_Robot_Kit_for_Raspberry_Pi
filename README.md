# 🤖 Freenove Big Hexapod Robot - Modernized

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%203.0-orange.svg)

Version modernisée du Freenove Big Hexapod Robot avec architecture microservices, API REST complète, logging structuré, et intégration Orion-SRE.

---

## 🚀 Nouveautés v2.1 (Phase 2)

### ✨ API REST Complète
- **15 endpoints** pour contrôle complet du robot
- **Validation Pydantic** sur toutes les requêtes
- **Documentation Swagger** interactive
- **26 tests automatisés** (89% coverage)

### 🎮 Endpoints disponibles

#### Movement Control
- POST /api/v1/movement/move - Déplacer le robot
- POST /api/v1/movement/stop - Arrêt d'urgence
- POST /api/v1/movement/attitude - Contrôle attitude (roll/pitch/yaw)
- POST /api/v1/movement/position - Contrôle position (x/y/z)
- GET /api/v1/movement/status - État du mouvement

#### Sensors
- GET /api/v1/sensors/imu - Données IMU (accéléromètre/gyroscope)
- GET /api/v1/sensors/ultrasonic - Distance ultrasonique
- GET /api/v1/sensors/battery - État batterie
- GET /api/v1/sensors/all - Tous les capteurs

#### Camera
- POST /api/v1/camera/rotate - Rotation caméra
- GET /api/v1/camera/config - Configuration caméra
- POST /api/v1/camera/config - Modifier configuration

#### LEDs
- POST /api/v1/leds/mode - Mode LED (off/solid/chase/blink/breathing/rainbow)
- POST /api/v1/leds/color - Couleur RGB

#### Buzzer
- POST /api/v1/buzzer/beep - Contrôle buzzer

---

## 📁 Structure du Projet

    .
    ├── api/                    # API REST FastAPI
    │   ├── main.py            # Application principale
    │   ├── models.py          # Modèles Pydantic
    │   └── routers/           # Endpoints modulaires
    │       ├── movement.py    # Contrôle mouvement
    │       ├── sensors.py     # Lecture capteurs
    │       ├── camera.py      # Contrôle caméra
    │       ├── leds.py        # Contrôle LEDs
    │       └── buzzer.py      # Contrôle buzzer
    ├── core/                   # Modules centraux
    │   ├── config.py          # Configuration Pydantic
    │   └── logger.py          # Logging structuré
    ├── features/               # Features modulaires
    │   ├── telemetry/         # Métriques (Phase 3)
    │   ├── autonomous/        # Navigation autonome (Phase 3)
    │   ├── vision/            # Computer vision (Phase 3)
    │   └── orion_bridge/      # Intégration Orion-SRE (Phase 4)
    ├── tests/                  # Tests (26 tests, 89% coverage)
    │   ├── unit/              # Tests unitaires
    │   └── integration/       # Tests d'intégration
    ├── config/                 # Fichiers de configuration
    ├── legacy/                 # Code original (backup)
    ├── docs/                   # Documentation
    └── Makefile               # Commandes de développement

---

## ⚙️ Installation

Installation identique à la Phase 1 (voir section complète dans le fichier).

---

## 🎮 Usage Rapide

    # Lancer le serveur
    make dev

    # Voir la documentation interactive
    # Ouvrir http://localhost:8000/docs

    # Exemple: Déplacer le robot
    curl -X POST http://localhost:8000/api/v1/movement/move \
      -H "Content-Type: application/json" \
      -d '{"mode":"motion","x":10,"y":5,"speed":7,"angle":0}'

    # Exemple: Lire les capteurs
    curl http://localhost:8000/api/v1/sensors/all

    # Exemple: Contrôler les LEDs
    curl -X POST http://localhost:8000/api/v1/leds/mode \
      -H "Content-Type: application/json" \
      -d '{"mode":"solid","color":{"red":255,"green":0,"blue":0}}'

---

## 🧪 Tests

    # Lancer tous les tests
    make test

    # Résultats: 26/26 tests passés, 89% coverage

---

## 📊 API Examples

### Déplacer le robot

    POST /api/v1/movement/move
    {
      "mode": "motion",
      "x": 10,
      "y": 5,
      "speed": 7,
      "angle": 0
    }

### Contrôler l'attitude

    POST /api/v1/movement/attitude
    {
      "roll": 5,
      "pitch": -3,
      "yaw": 0
    }

### Lire la batterie

    GET /api/v1/sensors/battery
    
    Response:
    {
      "voltage": 7.4,
      "percentage": 85,
      "is_low": false,
      "is_critical": false
    }

### Rotation caméra

    POST /api/v1/camera/rotate
    {
      "horizontal": 45,
      "vertical": -20
    }

---

## 🛣️ Roadmap

### Phase 1 : Fondations ✅ (TERMINÉ)
- [x] Restructuration du projet
- [x] Configuration moderne
- [x] Logging structuré
- [x] API FastAPI de base
- [x] Tests unitaires et intégration

### Phase 2 : API REST Complète ✅ (TERMINÉ)
- [x] Endpoints de mouvement
- [x] Endpoints caméra
- [x] Endpoints capteurs
- [x] Endpoints LEDs et buzzer
- [x] Validation Pydantic complète
- [x] 26 tests automatisés

### Phase 3 : Intelligence (Prochaine étape)
- [ ] Navigation autonome
- [ ] Évitement d'obstacles
- [ ] Computer vision (YOLOv8)
- [ ] QR code scanner
- [ ] WebSocket streaming vidéo

### Phase 4 : Intégration Orion-SRE
- [ ] Bridge Orion
- [ ] Export métriques vers Brain
- [ ] Auto-recovery via Healer
- [ ] Notifications via Narrator

### Phase 5 : Production
- [ ] Dockerisation
- [ ] CI/CD GitHub Actions
- [ ] Documentation complète

---

## 📝 License

Ce projet est sous licence CC BY-NC-SA 3.0.

---

## 🙏 Crédits

- **Freenove** - Kit robot original
- **Mars375** - Modernisation v2.x
- **FastAPI** - Framework web
- **Pydantic** - Validation

---

**Made with ❤️ for robotics and SRE**

---

## 🚀 Nouveautés v2.2 (Phase 3)

### ✨ Intelligence & Features Avancées

#### 🤖 Robot Controller
- Gestion unifiée de la communication TCP
- État du robot en temps réel
- Singleton pattern pour accès global

#### 📡 WebSocket Streaming
- GET /api/v1/ws/video - Streaming vidéo temps réel
- GET /api/v1/ws/sensors - Streaming données capteurs
- GET /api/v1/ws/test - Page de test WebSocket

#### 🧭 Navigation Autonome
- Évitement d'obstacles intelligent
- 4 niveaux de distance (safe, warning, unsafe, critical)
- Suggestions de manœuvres automatiques
- GET /api/v1/advanced/obstacle-avoidance/analyze?distance=X

#### 👁️ Computer Vision
- Intégration YOLOv8 (placeholder)
- Détection d'objets en temps réel
- GET /api/v1/advanced/vision/detect

#### 📱 QR Code Scanner
- Scanner QR codes depuis la caméra
- Décodage automatique
- GET /api/v1/advanced/vision/scan-qr

### 📊 Statistiques Phase 3

- 3 nouveaux endpoints WebSocket
- 3 endpoints advanced features
- 1 robot controller core
- 3 modules intelligence (obstacle, vision, qr)
- 10+ nouveaux tests

