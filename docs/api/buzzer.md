# Buzzer Control API

API endpoints pour contrôler le buzzer piézo du robot hexapode.

## ⚡ Architecture Non-Bloquante

**Le buzzer fonctionne en arrière-plan** via `asyncio.create_task()`, permettant au serveur de continuer à répondre aux autres requêtes pendant qu'un buzz est en cours.

### Caractéristiques:
- ✅ **Non-bloquant**: Le serveur répond instantanément
- ✅ **Multi-tâches**: Le robot peut bouger pendant que le buzzer sonne
- ✅ **Auto-cancellation**: Un nouveau beep arrête automatiquement le précédent
- ✅ **Contrôle**: Endpoint `/api/buzzer/stop` pour arrêter manuellement
- ✅ **Status en temps réel**: `/api/buzzer/status` indique si le buzzer est actif
- ✅ **Longue durée**: Jusqu'à 60 secondes de buzz continu

---

## Endpoints

### POST /api/buzzer/beep
Activer le buzzer avec une fréquence et une durée spécifiées. **S'exécute en arrière-plan (non-bloquant).**

**Request Body:**
```json
{
  "frequency": 1000,
  "duration": 5.0,
  "enabled": true
}
```

**Parameters:**
- `frequency` (int, 100-5000): Fréquence du son en Hz
- `duration` (float, 0.1-60.0): Durée du buzz en secondes (max 60s)
- `enabled` (bool): Activer/désactiver le beep (défaut: true)

**Response:**
```json
{
  "success": true,
  "message": "Buzzer started: 1000Hz for 5.0s",
  "data": {
    "frequency": 1000,
    "duration": 5.0
  }
}
```

**Comportement:**
- Si un buzz est déjà en cours, il sera **automatiquement annulé** et remplacé par le nouveau
- Le serveur répond immédiatement, le buzz continue en arrière-plan
- Le robot peut exécuter d'autres commandes pendant le buzz

---

### POST /api/buzzer/stop
⛔ Arrêter immédiatement le buzzer s'il est en cours d'exécution.

**Response (buzz en cours):**
```json
{
  "success": true,
  "message": "Buzzer stopped",
  "data": {
    "was_running": true
  }
}
```

**Response (pas de buzz):**
```json
{
  "success": true,
  "message": "Buzzer was not running",
  "data": {
    "was_running": false
  }
}
```

---

### GET /api/buzzer/status
Obtenir le statut actuel du buzzer.

**Response:**
```json
{
  "success": true,
  "message": "Buzzer status retrieved",
  "data": {
    "type": "buzzer",
    "pin": 17,
    "status": "ready",
    "available": true,
    "buzzing": true
  }
}
```

**Champs:**
- `type`: Type de composant ("buzzer")
- `pin`: Numéro GPIO utilisé
- `status`: État du composant ("ready", "error", etc.)
- `available`: Si le buzzer est disponible
- `buzzing`: **true** si un buzz est en cours, **false** sinon

---

## Error Codes

- **503 Service Unavailable**: Le buzzer n'est pas disponible (GPIO non initialisé)
- **500 Internal Server Error**: Échec de la commande buzzer

---

## Hardware Requirements

- Buzzer piézoélectrique
- GPIO 17 (BCM) sur Raspberry Pi
- Contrôle PWM (Pulse Width Modulation)

---

## Configuration GPIO

Le buzzer utilise **GPIO 17 (BCM)** en mode PWM.

**Vérifier l'état GPIO:**
```bash
gpio readall
```

**Test manuel (si besoin):**
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, 1000)  # 1000Hz
pwm.start(50)
time.sleep(1)
pwm.stop()
GPIO.cleanup()
```

---

## Examples

### Exemple 1: Beep court (notification)
```bash
curl -X POST http://localhost:8000/api/buzzer/beep \
  -H "Content-Type: application/json" \
  -d '{"frequency": 2000, "duration": 0.2, "enabled": true}'
```

### Exemple 2: Alarme longue (30 secondes)
```bash
curl -X POST http://localhost:8000/api/buzzer/beep \
  -H "Content-Type: application/json" \
  -d '{"frequency": 1500, "duration": 30.0, "enabled": true}'
```

### Exemple 3: Vérifier si le buzzer est actif
```bash
curl http://localhost:8000/api/buzzer/status
```

### Exemple 4: Arrêter le buzz en cours
```bash
curl -X POST http://localhost:8000/api/buzzer/stop
```

### Exemple 5: Désactiver le buzz (enabled=false)
```bash
curl -X POST http://localhost:8000/api/buzzer/beep \
  -H "Content-Type: application/json" \
  -d '{"frequency": 1000, "duration": 5.0, "enabled": false}'
```

---

## 🎵 Référence de Fréquences

### Notes Musicales
| Note | Fréquence (Hz) | Utilisation |
|------|----------------|-------------|
| Do (C4) | 262 | Note basse |
| Ré (D4) | 294 | |
| Mi (E4) | 330 | |
| Fa (F4) | 349 | |
| Sol (G4) | 392 | |
| La (A4) | 440 | Note de référence |
| Si (B4) | 494 | |
| Do (C5) | 523 | Note haute |

### Sons d'Alerte
| Type | Fréquence (Hz) | Description |
|------|----------------|-------------|
| **Basse** | 100-300 | Son grave, sérieux |
| **Médium** | 500-1000 | Son standard, neutre |
| **Haute** | 1500-2500 | Son aigu, urgent |
| **Très haute** | 3000-5000 | Son perçant, alerte |

### Recommandations
- **Notification**: 2000 Hz, 0.2s
- **Confirmation**: 1000 Hz, 0.1s
- **Avertissement**: 1500 Hz, 0.5s
- **Alarme**: 2500 Hz, 1.0s (répété)
- **Erreur**: 500 Hz, 0.3s

---

## 🎼 Créer des Mélodies

Pour créer des séquences de sons, enchaînez plusieurs beeps avec des délais :

**Mélodie simple (Do-Mi-Sol):**
```bash
# Do (262 Hz)
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 262, "duration": 0.3}'
sleep 0.4

# Mi (330 Hz)
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 330, "duration": 0.3}'
sleep 0.4

# Sol (392 Hz)
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 392, "duration": 0.3}'
```

**Sirène d'alarme (alternance de fréquences):**
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/buzzer/beep \
    -d '{"frequency": 1000, "duration": 0.2}'
  sleep 0.3
  curl -X POST http://localhost:8000/api/buzzer/beep \
    -d '{"frequency": 1500, "duration": 0.2}'
  sleep 0.3
done
```

---

## 🎯 Workflow Typique

### 1. Notification Simple
```bash
# Beep court pour confirmer une action
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 2000, "duration": 0.15}'
```

### 2. Alarme avec Arrêt Manuel
```bash
# Démarrer une alarme longue (30s)
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 1500, "duration": 30.0}'

# Vérifier qu'elle tourne
curl http://localhost:8000/api/buzzer/status
# → "buzzing": true

# Arrêter manuellement après quelques secondes
curl -X POST http://localhost:8000/api/buzzer/stop
```

### 3. Remplacement Automatique
```bash
# Démarrer un buzz long
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 1000, "duration": 10.0}'

# Immédiatement après, changer pour un autre son
# L'ancien sera automatiquement annulé
curl -X POST http://localhost:8000/api/buzzer/beep \
  -d '{"frequency": 2000, "duration": 2.0}'
```

### 4. Séquence d'Initialisation
```bash
# Triple beep pour indiquer démarrage réussi
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/buzzer/beep \
    -d '{"frequency": 1000, "duration": 0.1}'
  sleep 0.2
done
```

---

## 📊 Comparaison Durées

| Durée | Usage | Exemple |
|-------|-------|----------|
| **0.1s** | Click / confirmation rapide | Bouton pressé |
| **0.2s** | Notification standard | Message reçu |
| **0.5s** | Avertissement court | Batterie faible |
| **1.0s** | Alerte | Obstacle détecté |
| **5.0s** | Alarme modérée | Perte de connexion |
| **30.0s** | Alarme longue | Situation critique |
| **60.0s** | Maximum autorisé | Test ou urgence |

---

## 💡 Bonnes Pratiques

### ✅ À Faire
- Utiliser des beeps courts (< 1s) pour les notifications
- Vérifier le status avant d'arrêter un buzz
- Utiliser des fréquences > 1000 Hz pour une meilleure audibilité
- Tester les fréquences pour trouver le son optimal

### ❌ À Éviter
- Ne pas créer de boucles infinies de beeps
- Éviter les fréquences < 500 Hz (difficiles à entendre)
- Ne pas utiliser `duration=60s` en production (réservé aux tests)
- Ne pas envoyer de requêtes trop rapprochées (< 0.1s d'intervalle)

---

## 🔧 Dépannage

### Le buzzer ne fait aucun bruit
1. Vérifier que GPIO 17 est bien configuré
2. Vérifier les connexions du buzzer
3. Tester avec `/api/buzzer/status` → `available` doit être `true`
4. Vérifier les permissions GPIO

### Le son est trop faible
- Augmenter la fréquence (1500-2500 Hz)
- Vérifier l'alimentation du buzzer
- Tester avec un buzzer actif au lieu de passif

### Le buzz continue après la durée prévue
- Utiliser `/api/buzzer/stop` pour forcer l'arrêt
- Redémarrer le service si le problème persiste

### "Buzzer not available"
- RPi.GPIO n'est pas installé
- MOCK_HARDWARE est activé dans les settings
- Le GPIO 17 est utilisé par un autre processus

---

## 🎓 Exemples Avancés

### Script Python: Alarme Progressive
```python
import requests
import time

BASE_URL = "http://localhost:8000/api/buzzer"

# Alarme qui augmente en fréquence
for freq in [500, 1000, 1500, 2000, 2500]:
    requests.post(f"{BASE_URL}/beep", json={
        "frequency": freq,
        "duration": 0.3
    })
    time.sleep(0.4)
```

### Script Bash: Morse Code (SOS)
```bash
#!/bin/bash
BASE_URL="http://localhost:8000/api/buzzer/beep"

# S (3 courts)
for i in {1..3}; do
  curl -X POST $BASE_URL -d '{"frequency": 1000, "duration": 0.2}'
  sleep 0.3
done

sleep 0.5

# O (3 longs)
for i in {1..3}; do
  curl -X POST $BASE_URL -d '{"frequency": 1000, "duration": 0.6}'
  sleep 0.7
done

sleep 0.5

# S (3 courts)
for i in {1..3}; do
  curl -X POST $BASE_URL -d '{"frequency": 1000, "duration": 0.2}'
  sleep 0.3
done
```

### WebSocket Integration
```javascript
// Déclencher un beep depuis le frontend
const beep = async (frequency, duration) => {
  const response = await fetch('/api/buzzer/beep', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frequency, duration, enabled: true })
  });
  return response.json();
};

// Notification sonore sur événement
beep(2000, 0.2); // Beep rapide
```

---

## 📚 Voir Aussi

- [LED Control API](./leds.md) - Combiner sons et lumières
- [Movement API](./movement.md) - Synchroniser mouvements et sons
- [Sensors API](./sensors.md) - Déclencher alarmes sur événements
