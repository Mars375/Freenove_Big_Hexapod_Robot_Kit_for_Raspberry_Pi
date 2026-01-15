# LED Control API

API endpoints pour contrôler le bandeau LED WS2812B (8 LEDs) du robot hexapode.

## Endpoints

### POST /api/leds/color
Définir une couleur fixe sur toutes les LEDs.

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
Lancer l'animation arc-en-ciel.

**Request Body:**
```json
{
  "iterations": 2
}
```

**Parameters:**
- iterations (int): Nombre de cycles complets

**Response:**
```json
{
  "success": true,
  "message": "Rainbow animation started for 2 iterations",
  "data": {
    "iterations": 2
  }
}
```

---

### POST /api/leds/police
Lancer l'animation sirène de police (rouge/bleu alternant).

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
Lancer l'animation respiration (fade in/out).

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
Lancer l'animation feu (scintillement rouge/orange/jaune).

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
Lancer l'animation vague (propagation de couleur).

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
Lancer l'animation stroboscope (flash rapide on/off).

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
Lancer l'animation poursuite (LEDs qui courent en séquence).

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

### POST /api/leds/off
Éteindre toutes les LEDs.

**Response:**
```json
{
  "success": true,
  "message": "LEDs turned off"
}
```

---

### GET /api/leds/status
Obtenir le statut actuel du bandeau LED.

**Response:**
```json
{
  "success": true,
  "message": "LED status retrieved successfully",
  "data": {
    "available": true,
    "led_count": 8,
    "brightness": 255,
    "current_mode": "OFF",
    "current_color": [0, 0, 0]
  }
}
```

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

**Exemple: Couleur rouge fixe**
```bash
curl -X POST http://localhost:8000/api/leds/color \
  -H "Content-Type: application/json" \
  -d '{"r": 255, "g": 0, "b": 0}'
```

**Exemple: Éteindre les LEDs**
```bash
curl -X POST http://localhost:8000/api/leds/off
```

---

## Animation Details

### Police
- Moitié rouge / moitié bleue qui alternent
- Vitesse ajustable (0.05-1.0s recommandé)

### Breathing
- Fade progressif entre éteint et couleur pleine
- Speed = cycles par seconde (0.5-3.0 recommandé)

### Fire
- Scintillement aléatoire rouge/orange
- Intensity contrôle la vivacité (0.5-1.0 recommandé)

### Wave
- Vague de couleur se propageant sur les LEDs
- Speed contrôle la vitesse de propagation

### Strobe
- Flash rapide on/off
- Speed très rapide (0.01-0.1s recommandé)

### Chase
- LED unique qui court avec traînée
- Speed contrôle la vitesse de déplacement (0.05-0.2s recommandé)
