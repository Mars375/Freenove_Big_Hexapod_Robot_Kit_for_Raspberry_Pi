# LED Control API

API endpoints pour contrôler le bandeau LED WS2812B (8 LEDs) du robot hexapode.

## ⚡ Architecture Non-Bloquante

**Toutes les animations s'exécutent en arrière-plan** via `asyncio.create_task()`, permettant au serveur de continuer à répondre aux autres requêtes pendant qu'une animation tourne.

### Caractéristiques:
- ✅ **Non-bloquant**: Le serveur répond instantanément
- ✅ **Multi-tâches**: Le robot peut bouger pendant que les LEDs animent
- ✅ **Auto-cancellation**: Lancer une nouvelle animation arrête automatiquement la précédente
- ✅ **Contrôle**: Endpoint `/api/leds/stop` pour arrêter manuellement
- ✅ **Status en temps réel**: `/api/leds/status` indique l'animation en cours

---

## Endpoints

### POST /api/leds/color
Définir une couleur fixe sur toutes les LEDs. **Arrête toute animation en cours.**

**Request Body:**
```json
{
  "r": 255,
  "g": 0,
  "b": 0
}
```

**Parameters:**
- r (int, 0-255): Intensité rouge
- g (int, 0-255): Intensité verte
- b (int, 0-255): Intensité bleue

**Response:**
```json
{
  "success": true,
  "message": "LED color set successfully",
  "data": {
    "color": [255, 0, 0]
  }
}
```

---

### POST /api/leds/brightness
Ajuster la luminosité globale des LEDs.

**Request Body:**
```json
{
  "brightness": 128
}
```

**Parameters:**
- brightness (int, 0-255): Niveau de luminosité (0=éteint, 255=maximum)

**Response:**
```json
{
  "success": true,
  "message": "LED brightness set to 128",
  "data": {
    "brightness": 128
  }
}
```

---

### POST /api/leds/rainbow
Lancer l'animation arc-en-ciel **en arrière-plan**. Chaque LED affiche une couleur différente, créant une roue chromatique qui tourne.

**Request Body:**
```json
{
  "duration": 10.0,
  "speed": 0.05
}
```

**Parameters:**
- duration (float, 1.0-3600.0): Durée totale en secondes (défaut: 10.0)
- speed (float, 0.01-1.0): Vitesse de rotation en secondes (défaut: 0.05, plus petit = plus rapide)

**Response:**
```json
{
  "success": true,
  "message": "Rainbow animation started for 10.0s",
  "data": {
    "duration": 10.0,
    "speed": 0.05
  }
}
```

**Effet visuel:**
- LED 0: 🔴 Rouge
- LED 1: 🟠 Orange
- LED 2: 🟡 Jaune
- LED 3: 🟢 Vert
- LED 4: 🔵 Bleu
- LED 5: 🟣 Violet
- LED 6: 🟣 Magenta
- LED 7: 🔴 Rouge

La roue chromatique **tourne en continu** pendant la durée spécifiée.

---

### POST /api/leds/police
Lancer l'animation sirène de police **en arrière-plan** (rouge/bleu alternant).

**Request Body:**
```json
{
  "duration": 5.0,
  "speed": 0.1
}
```

**Parameters:**
- duration (float): Durée totale en secondes
- speed (float): Vitesse de clignotement en secondes

**Response:**
```json
{
  "success": true,
  "message": "Police animation started for 5.0s",
  "data": {
    "duration": 5.0,
    "speed": 0.1
  }
}
```

---

### POST /api/leds/breathing
Lancer l'animation respiration **en arrière-plan** (fade in/out).

**Request Body:**
```json
{
  "r": 0,
  "g": 0,
  "b": 255,
  "duration": 10.0,
  "speed": 2.0
}
```

**Parameters:**
- r (int, 0-255): Intensité rouge
- g (int, 0-255): Intensité verte
- b (int, 0-255): Intensité bleue
- duration (float): Durée totale en secondes
- speed (float): Cycles de respiration par seconde

**Response:**
```json
{
  "success": true,
  "message": "Breathing animation started for 10.0s",
  "data": {
    "color": [0, 0, 255],
    "duration": 10.0,
    "speed": 2.0
  }
}
```

---

### POST /api/leds/fire
Lancer l'animation feu **en arrière-plan** (scintillement rouge/orange/jaune).

**Request Body:**
```json
{
  "duration": 10.0,
  "intensity": 1.0
}
```

**Parameters:**
- duration (float): Durée totale en secondes
- intensity (float, 0.1-1.0): Intensité du feu

**Response:**
```json
{
  "success": true,
  "message": "Fire animation started for 10.0s",
  "data": {
    "duration": 10.0,
    "intensity": 1.0
  }
}
```

---

### POST /api/leds/wave
Lancer l'animation vague **en arrière-plan** (propagation de couleur).

**Request Body:**
```json
{
  "r": 0,
  "g": 255,
  "b": 0,
  "duration": 10.0,
  "speed": 0.5
}
```

**Parameters:**
- r (int, 0-255): Intensité rouge
- g (int, 0-255): Intensité verte
- b (int, 0-255): Intensité bleue
- duration (float): Durée totale en secondes
- speed (float): Vitesse de la vague

**Response:**
```json
{
  "success": true,
  "message": "Wave animation started for 10.0s",
  "data": {
    "color": [0, 255, 0],
    "duration": 10.0,
    "speed": 0.5
  }
}
```

---

### POST /api/leds/strobe
Lancer l'animation stroboscope **en arrière-plan** (flash rapide on/off).

**Request Body:**
```json
{
  "r": 255,
  "g": 255,
  "b": 255,
  "duration": 5.0,
  "speed": 0.05
}
```

**Parameters:**
- r (int, 0-255): Intensité rouge
- g (int, 0-255): Intensité verte
- b (int, 0-255): Intensité bleue
- duration (float): Durée totale en secondes
- speed (float): Vitesse des flashs en secondes

**Response:**
```json
{
  "success": true,
  "message": "Strobe animation started for 5.0s",
  "data": {
    "color": [255, 255, 255],
    "duration": 5.0,
    "speed": 0.05
  }
}
```

---

### POST /api/leds/chase
Lancer l'animation poursuite **en arrière-plan** (LEDs qui courent en séquence).

**Request Body:**
```json
{
  "r": 255,
  "g": 0,
  "b": 0,
  "duration": 10.0,
  "speed": 0.1
}
```

**Parameters:**
- r (int, 0-255): Intensité rouge
- g (int, 0-255): Intensité verte
- b (int, 0-255): Intensité bleue
- duration (float): Durée totale en secondes
- speed (float): Vitesse de la poursuite

**Response:**
```json
{
  "success": true,
  "message": "Chase animation started for 10.0s",
  "data": {
    "color": [255, 0, 0],
    "duration": 10.0,
    "speed": 0.1
  }
}
```

---

### POST /api/leds/stop
⚡ **Nouveau!** Arrêter l'animation en cours d'exécution.

**Response:**
```json
{
  "success": true,
  "message": "Animation 'rainbow' stopped",
  "data": {
    "stopped_animation": "rainbow"
  }
}
```

**Ou si aucune animation ne tourne:**
```json
{
  "success": true,
  "message": "No animation running",
  "data": {
    "stopped_animation": null
  }
}
```

---

### POST /api/leds/off
Éteindre toutes les LEDs. **Arrête toute animation en cours.**

**Response:**
```json
{
  "success": true,
  "message": "LEDs turned off"
}
```

---

### GET /api/leds/status
Obtenir le statut actuel du bandeau LED **incluant l'état de l'animation**.

**Response:**
```json
{
  "success": true,
  "message": "LED status retrieved successfully",
  "data": {
    "type": "led_strip",
    "led_count": 8,
    "brightness": 255,
    "sequence": "GRB",
    "bus": 0,
    "device": 0,
    "status": "ready",
    "available": true,
    "current_color": [0, 0, 0],
    "current_mode": "RAINBOW",
    "mock_mode": false,
    "animation_running": true,
    "current_animation": "rainbow"
  }
}
```

**Nouveaux champs:**
- `animation_running` (bool): True si une animation est en cours
- `current_animation` (string|null): Nom de l'animation en cours ("rainbow", "police", "fire", etc.) ou null

---

## Error Codes

- **503 Service Unavailable**: Le bandeau LED n'est pas disponible (SPI non initialisé)
- **500 Internal Server Error**: Échec de l'animation ou de la commande

---

## Hardware Requirements

- Bandeau LED WS2812B (8 LEDs)
- Interface SPI activée sur Raspberry Pi
- Bus SPI: /dev/spidev0.0

---

## Configuration SPI

Pour activer SPI sur Raspberry Pi:

```bash
sudo raspi-config
```

Aller dans **Interface Options > SPI > Enable**

Ou ajouter dans `/boot/firmware/config.txt`:

```
dtparam=spi=on
```

---

## Examples

**Exemple: Rainbow pendant 1 heure**
```bash
curl -X POST http://localhost:8000/api/leds/rainbow \
  -H "Content-Type: application/json" \
  -d '{"duration": 3600.0, "speed": 0.05}'
```

**Exemple: Police siren 3 secondes**
```bash
curl -X POST http://localhost:8000/api/leds/police \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "speed": 0.1}'
```

**Exemple: Breathing bleu 10 secondes**
```bash
curl -X POST http://localhost:8000/api/leds/breathing \
  -H "Content-Type: application/json" \
  -d '{"r": 0, "g": 0, "b": 255, "duration": 10.0, "speed": 1.0}'
```

**Exemple: Arrêter animation en cours**
```bash
curl -X POST http://localhost:8000/api/leds/stop
```

**Exemple: Vérifier le status et l'animation en cours**
```bash
curl -X GET http://localhost:8000/api/leds/status
```

**Exemple: Couleur rouge fixe (arrête l'animation)**
```bash
curl -X POST http://localhost:8000/api/leds/color \
  -H "Content-Type: application/json" \
  -d '{"r": 255, "g": 0, "b": 0}'
```

**Exemple: Éteindre les LEDs (arrête l'animation)**
```bash
curl -X POST http://localhost:8000/api/leds/off
```

---

## Animation Details

### Rainbow
- **Effet**: Roue chromatique tournante, chaque LED a une couleur différente
- **Speed**: Vitesse de rotation (0.01=très rapide, 0.1=lent)
- **Duration**: Peut tourner jusqu'à 1 heure (3600s)
- **Recommandé**: speed=0.05 pour une rotation fluide

### Police
- **Effet**: Moitié rouge / moitié bleue qui alternent
- **Speed**: Vitesse d'alternance (0.05-1.0s recommandé)

### Breathing
- **Effet**: Fade progressif entre éteint et couleur pleine
- **Speed**: Cycles par seconde (0.5-3.0 recommandé)

### Fire
- **Effet**: Scintillement aléatoire rouge/orange
- **Intensity**: Contrôle la vivacité (0.5-1.0 recommandé)

### Wave
- **Effet**: Vague de couleur se propageant sur les LEDs
- **Speed**: Contrôle la vitesse de propagation

### Strobe
- **Effet**: Flash rapide on/off
- **Speed**: Très rapide (0.01-0.1s recommandé)

### Chase
- **Effet**: LED unique qui court avec traînée
- **Speed**: Vitesse de déplacement (0.05-0.2s recommandé)

---

## 🎯 Workflow Typique

1. **Lancer une animation longue durée** (ex: rainbow 1h)
   ```bash
   curl -X POST http://localhost:8000/api/leds/rainbow \
     -d '{"duration": 3600.0, "speed": 0.05}'
   ```

2. **Le robot peut continuer à fonctionner normalement** (mouvements, capteurs, etc.)

3. **Vérifier l'animation en cours**
   ```bash
   curl -X GET http://localhost:8000/api/leds/status
   # → "animation_running": true, "current_animation": "rainbow"
   ```

4. **Changer d'animation** (arrête automatiquement la précédente)
   ```bash
   curl -X POST http://localhost:8000/api/leds/fire \
     -d '{"duration": 60.0}'
   ```

5. **Arrêter manuellement**
   ```bash
   curl -X POST http://localhost:8000/api/leds/stop
   ```
