# 🤖 Freenove Big Hexapod Robot - Modernized

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Tests](https://img.shields.io/badge/tests-10%20passed-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%203.0-orange.svg)

Version modernisée du Freenove Big Hexapod Robot avec architecture microservices, API REST, logging structuré, et intégration Orion-SRE.

---

## 🚀 Changements Majeurs (v2.0)

### ✨ Nouvelles Features
- **API REST moderne** avec FastAPI
- **Logging structuré** avec structlog (JSON pour production)
- **Configuration externalisée** avec Pydantic Settings
- **Tests automatisés** avec pytest (98% coverage)
- **Hot reload** en développement
- **Métriques Prometheus** ready
- **Health checks** pour monitoring
- **CORS configuré** pour applications web

### 🏗️ Architecture

Ancien (v1.x):           Nouveau (v2.0):
┌─────────────┐          ┌──────────────┐
│  Monolithe  │          │   FastAPI    │
│   PyQt5     │   →      │   REST API   │
│ Threading   │          │    asyncio   │
└─────────────┘          └──────────────┘
                         ┌──────────────┐
                         │  Core Modules│
                         │ Config+Logger│
                         └──────────────┘
                         ┌──────────────┐
                         │   Features   │
                         │  (modulaires)│
                         └──────────────┘

---

## 📁 Structure du Projet

    .
    ├── api/                    # API REST FastAPI
    │   ├── main.py            # Application principale
    │   └── routers/           # Endpoints modulaires (à venir)
    ├── core/                   # Modules centraux
    │   ├── config.py          # Configuration Pydantic
    │   └── logger.py          # Logging structuré
    ├── features/               # Features modulaires
    │   ├── telemetry/         # Métriques et monitoring
    │   ├── autonomous/        # Navigation autonome
    │   ├── vision/            # Computer vision
    │   └── orion_bridge/      # Intégration Orion-SRE
    ├── tests/                  # Tests unitaires et intégration
    │   ├── unit/              # Tests unitaires
    │   └── integration/       # Tests d'intégration
    ├── config/                 # Fichiers de configuration
    │   ├── config.yaml        # Config application
    │   └── logging.yaml       # Config logging
    ├── legacy/                 # Code original (backup)
    │   └── Code/              # Code Freenove original
    ├── docs/                   # Documentation
    ├── logs/                   # Logs (gitignored)
    ├── .env                    # Variables d'environnement (gitignored)
    ├── .env.example           # Template de configuration
    ├── pyproject.toml         # Configuration Poetry
    ├── requirements.txt       # Dépendances pip
    └── Makefile              # Commandes de développement

---

## ⚙️ Installation

### Prérequis
- Python 3.11+
- Poetry (recommandé) ou pip
- Raspberry Pi OS (pour le robot physique)

### 1. Cloner le repository

    git clone https://github.com/Mars375/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi.git
    cd Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi

### 2. Installer les dépendances

**Avec Poetry (recommandé):**

    # Installer Poetry
    pipx install poetry

    # Installer les dépendances
    poetry install

    # Activer l'environnement
    source $(poetry env info --path)/bin/activate

**Avec pip:**

    # Créer un environnement virtuel
    python3 -m venv venv
    source venv/bin/activate

    # Installer les dépendances
    pip install -r requirements.txt

### 3. Configurer l'environnement

    # Copier le fichier de configuration
    cp .env.example .env

    # Éditer .env avec vos paramètres
    nano .env

---

## 🎮 Usage

### Développement

    # Lancer le serveur de développement (avec hot reload)
    make dev

    # Ou avec uvicorn directement
    uvicorn api.main:app --reload

Le serveur démarre sur http://localhost:8000

**Endpoints disponibles:**
- GET / - Informations de base
- GET /health - Health check (pour monitoring)
- GET /metrics - Métriques Prometheus
- GET /docs - Documentation Swagger UI interactive
- GET /redoc - Documentation ReDoc

### Tests

    # Lancer tous les tests
    make test

    # Avec couverture de code
    pytest --cov=. --cov-report=html

    # Voir le rapport HTML
    open htmlcov/index.html

### Autres commandes

    # Voir toutes les commandes disponibles
    make help

    # Formater le code
    make format

    # Linter
    make lint

    # Nettoyer les fichiers cache
    make clean

---

## 🧪 Tests

Le projet utilise pytest avec une couverture de 98%.

    # Tests unitaires uniquement
    pytest tests/unit/

    # Tests d'intégration uniquement
    pytest tests/integration/

    # Tests avec verbosité
    pytest -v

    # Tests avec couverture détaillée
    pytest --cov=. --cov-report=term-missing

**Résultats actuels:**
- ✅ 10/10 tests passés
- ✅ 98% de couverture
- ✅ Tous les modules core testés

---

## 📊 Monitoring & Observabilité

### Logs structurés

Les logs sont au format JSON en production et colorés en développement.

Exemple Python:

    from core.logger import get_logger

    logger = get_logger(__name__)
    logger.info("robot.movement", x=10, y=5, speed=7, angle=0)

Output JSON:

    {
      "event": "robot.movement",
      "timestamp": "2026-01-13T15:00:00.000000Z",
      "level": "info",
      "app": "hexapod-robot",
      "version": "2.0.0",
      "environment": "production",
      "robot": "Hexapod-01",
      "x": 10,
      "y": 5,
      "speed": 7,
      "angle": 0
    }

### Health Check

    curl http://localhost:8000/health

Réponse:

    {
      "status": "healthy",
      "robot": "Hexapod-01",
      "version": "2.0.0",
      "camera_enabled": true,
      "imu_enabled": true,
      "ultrasonic_enabled": true
    }

---

## 🔧 Configuration

La configuration utilise Pydantic Settings et peut être définie via:
1. Variables d'environnement
2. Fichier .env
3. Valeurs par défaut

### Variables principales

| Variable | Description | Défaut |
|----------|-------------|--------|
| APP_NAME | Nom de l'application | hexapod-robot |
| ENVIRONMENT | Environnement (dev/staging/prod) | development |
| API_PORT | Port de l'API REST | 8000 |
| LOG_LEVEL | Niveau de log | INFO |
| ROBOT_NAME | Nom du robot | Hexapod-01 |
| ORION_BRAIN_URL | URL Orion Brain | http://localhost:9000 |

Voir .env.example pour la liste complète.

---

## 🛣️ Roadmap

### Phase 1 : Fondations ✅ (TERMINÉ)
- [x] Restructuration du projet
- [x] Configuration moderne
- [x] Logging structuré
- [x] API FastAPI de base
- [x] Tests unitaires et intégration

### Phase 2 : API REST Complète (Prochaine étape)
- [ ] Endpoints de mouvement
- [ ] Endpoints caméra
- [ ] Endpoints capteurs
- [ ] WebSocket pour streaming
- [ ] Authentication JWT

### Phase 3 : Intelligence
- [ ] Navigation autonome
- [ ] Évitement d'obstacles
- [ ] Computer vision (YOLOv8)
- [ ] QR code scanner

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

## 🤝 Contribution

Ce projet est un fork du [Freenove Big Hexapod Robot Kit](https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi) avec des améliorations modernes.

### Développement

1. Créer une branche feature

    git checkout -b feature/ma-feature

2. Développer avec les tests

    make dev  # Terminal 1
    make test # Terminal 2

3. Commiter avec des messages conventionnels

    git commit -m "feat: add new feature"
    git commit -m "fix: correct bug"
    git commit -m "test: add tests"

4. Push et créer une PR

    git push origin feature/ma-feature

---

## 📝 License

Ce projet est sous licence CC BY-NC-SA 3.0.

- ✅ Usage personnel et éducatif
- ❌ Usage commercial interdit
- ✅ Modifications autorisées
- ✅ Partage autorisé (même licence)

---

## 🙏 Crédits

- **Freenove** - Kit robot original et hardware
- **Mars375** - Modernisation et architecture v2.0
- **FastAPI** - Framework web moderne
- **Pydantic** - Validation et configuration
- **Pytest** - Framework de tests

---

## 📧 Contact

- GitHub: @Mars375
- Projet Orion-SRE: https://github.com/Mars375/Orion-SRE

---

**Made with ❤️ for robotics and SRE**
