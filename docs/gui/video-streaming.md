# Video Streaming Integration Guide

Guide complet pour intégrer le flux vidéo de la caméra du robot hexapode dans votre interface graphique (GUI).

---

## 📹 Vue d'Ensemble

Le robot hexapode Tachikoma est équipé d'une **caméra Raspberry Pi** qui diffuse en temps réel via plusieurs protocoles de streaming :

- **MJPEG Stream** (Motion JPEG) - Simple, faible latence
- **HLS** (HTTP Live Streaming) - Adaptative, compatible mobile
- **WebRTC** (optionnel) - Très faible latence, bidirectionnel

---

## 🎯 Architecture du Streaming

```
┌─────────────────┐
│   Raspberry Pi  │
│   (Tachikoma)   │
│                 │
│  ┌───────────┐  │
│  │  Camera   │  │
│  │  Module   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  picamera │  │
│  │  capture  │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  FastAPI  │  │
│  │  /stream  │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │
    HTTP/WebSocket
         │
┌────────▼────────┐
│   Web Browser   │
│                 │
│  ┌───────────┐  │
│  │    GUI    │  │
│  │  (React/  │  │
│  │   Vue.js) │  │
│  └───────────┘  │
└─────────────────┘
```

---

## 📡 Endpoints API Vidéo

### 1. Stream MJPEG (Recommandé pour GUI)

**Endpoint:** `GET /api/camera/stream`

**Description:** Flux MJPEG continu, idéal pour affichage en temps réel.

**Content-Type:** `multipart/x-mixed-replace; boundary=frame`

**Utilisation:**
```html
<img src="http://192.168.1.100:8000/api/camera/stream" />
```

---

### 2. Snapshot (Image unique)

**Endpoint:** `GET /api/camera/snapshot`

**Description:** Capture une seule image.

**Content-Type:** `image/jpeg`

**Utilisation:**
```javascript
fetch('http://192.168.1.100:8000/api/camera/snapshot')
  .then(response => response.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    document.getElementById('snapshot').src = url;
  });
```

---

### 3. Contrôle de la Caméra

**Endpoint:** `POST /api/camera/settings`

**Body:**
```json
{
  "resolution": [640, 480],
  "framerate": 30,
  "brightness": 50,
  "contrast": 0,
  "rotation": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Camera settings updated",
  "data": {
    "resolution": [640, 480],
    "framerate": 30
  }
}
```

---

## 🌐 Intégration dans différents frameworks

### ⚛️ React / Next.js

#### Composant VideoStream simple

```jsx
import React, { useState, useRef, useEffect } from 'react';

const VideoStream = ({ robotIP = '192.168.1.100' }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef(null);
  
  const streamUrl = `http://${robotIP}:8000/api/camera/stream`;
  
  const handleLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };
  
  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };
  
  return (
    <div className="video-container">
      {isLoading && <div className="loading">Chargement du flux...</div>}
      {hasError && (
        <div className="error">
          ❌ Impossible de se connecter à la caméra
        </div>
      )}
      <img
        ref={imgRef}
        src={streamUrl}
        alt="Robot Camera Stream"
        onLoad={handleLoad}
        onError={handleError}
        style={{ display: hasError ? 'none' : 'block' }}
      />
    </div>
  );
};

export default VideoStream;
```

#### CSS associé

```css
.video-container {
  position: relative;
  width: 100%;
  max-width: 640px;
  aspect-ratio: 4/3;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.loading, .error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  text-align: center;
}
```

---

#### Composant avancé avec contrôles

```jsx
import React, { useState, useRef } from 'react';
import axios from 'axios';

const AdvancedVideoStream = ({ robotIP = '192.168.1.100' }) => {
  const [settings, setSettings] = useState({
    resolution: [640, 480],
    framerate: 30,
    brightness: 50,
    rotation: 0
  });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);
  
  const streamUrl = `http://${robotIP}:8000/api/camera/stream`;
  const apiUrl = `http://${robotIP}:8000/api/camera`;
  
  const updateSettings = async (newSettings) => {
    try {
      await axios.post(`${apiUrl}/settings`, newSettings);
      setSettings({ ...settings, ...newSettings });
    } catch (error) {
      console.error('Failed to update camera settings:', error);
    }
  };
  
  const takeSnapshot = async () => {
    try {
      const response = await axios.get(`${apiUrl}/snapshot`, {
        responseType: 'blob'
      });
      const url = URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tachikoma-${Date.now()}.jpg`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to take snapshot:', error);
    }
  };
  
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setIsFullscreen(!isFullscreen);
  };
  
  return (
    <div ref={containerRef} className="advanced-video-container">
      {/* Stream vidéo */}
      <img src={streamUrl} alt="Robot Camera" />
      
      {/* Contrôles */}
      <div className="controls">
        <button onClick={takeSnapshot}>📷 Snapshot</button>
        <button onClick={toggleFullscreen}>
          {isFullscreen ? '🗗 Sortir' : '⛶ Plein écran'}
        </button>
        
        <div className="settings">
          <label>
            Luminosité:
            <input
              type="range"
              min="0"
              max="100"
              value={settings.brightness}
              onChange={(e) => 
                updateSettings({ brightness: parseInt(e.target.value) })
              }
            />
          </label>
          
          <label>
            Rotation:
            <select
              value={settings.rotation}
              onChange={(e) => 
                updateSettings({ rotation: parseInt(e.target.value) })
              }
            >
              <option value="0">0°</option>
              <option value="90">90°</option>
              <option value="180">180°</option>
              <option value="270">270°</option>
            </select>
          </label>
        </div>
      </div>
    </div>
  );
};

export default AdvancedVideoStream;
```

---

### 🖼️ Vue.js

#### Composant VideoStream.vue

```vue
<template>
  <div class="video-stream">
    <div v-if="loading" class="loading">
      Chargement du flux vidéo...
    </div>
    <div v-else-if="error" class="error">
      ❌ Erreur: {{ error }}
    </div>
    <img
      v-else
      :src="streamUrl"
      @load="onLoad"
      @error="onError"
      alt="Robot Camera Stream"
    />
    
    <div class="controls" v-if="!error">
      <button @click="takeSnapshot">📷 Capture</button>
      <button @click="toggleFullscreen">⛶ Plein écran</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoStream',
  props: {
    robotIP: {
      type: String,
      default: '192.168.1.100'
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      isFullscreen: false
    };
  },
  computed: {
    streamUrl() {
      return `http://${this.robotIP}:8000/api/camera/stream`;
    },
    apiUrl() {
      return `http://${this.robotIP}:8000/api/camera`;
    }
  },
  methods: {
    onLoad() {
      this.loading = false;
      this.error = null;
    },
    onError() {
      this.loading = false;
      this.error = 'Impossible de se connecter à la caméra';
    },
    async takeSnapshot() {
      try {
        const response = await fetch(`${this.apiUrl}/snapshot`);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `snapshot-${Date.now()}.jpg`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error('Snapshot failed:', err);
      }
    },
    toggleFullscreen() {
      if (!this.isFullscreen) {
        this.$el.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
      this.isFullscreen = !this.isFullscreen;
    }
  }
};
</script>

<style scoped>
.video-stream {
  position: relative;
  width: 100%;
  max-width: 640px;
  background: #000;
  border-radius: 8px;
}

.video-stream img {
  width: 100%;
  height: auto;
  display: block;
}

.controls {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
}

.controls button {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.controls button:hover {
  background: rgba(0, 0, 0, 0.9);
}
</style>
```

---

### 📄 Vanilla JavaScript

#### HTML

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Tachikoma Camera Stream</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      background: #1a1a1a;
      font-family: Arial, sans-serif;
    }
    
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    
    h1 {
      color: white;
      text-align: center;
    }
    
    .video-wrapper {
      position: relative;
      background: #000;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    #stream {
      width: 100%;
      display: block;
    }
    
    .overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 18px;
    }
    
    .controls {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
    }
    
    button {
      background: #0066cc;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      transition: background 0.2s;
    }
    
    button:hover {
      background: #0052a3;
    }
    
    button:disabled {
      background: #666;
      cursor: not-allowed;
    }
    
    .settings {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      margin-top: 20px;
    }
    
    .setting-group {
      margin-bottom: 15px;
    }
    
    .setting-group label {
      color: white;
      display: block;
      margin-bottom: 5px;
    }
    
    .setting-group input,
    .setting-group select {
      width: 100%;
      padding: 8px;
      border-radius: 4px;
      border: 1px solid #444;
      background: #333;
      color: white;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🤖 Tachikoma Camera Stream</h1>
    
    <div class="video-wrapper">
      <img id="stream" alt="Robot Camera Stream">
      <div id="overlay" class="overlay" style="display: flex;">
        Chargement du flux...
      </div>
    </div>
    
    <div class="controls">
      <button id="snapshot">📷 Prendre une photo</button>
      <button id="fullscreen">⛶ Plein écran</button>
      <button id="reconnect">🔄 Reconnecter</button>
    </div>
    
    <div class="settings">
      <h3 style="color: white;">⚙️ Paramètres</h3>
      
      <div class="setting-group">
        <label>Adresse IP du robot:</label>
        <input type="text" id="robotIP" value="192.168.1.100">
      </div>
      
      <div class="setting-group">
        <label>Luminosité (0-100):</label>
        <input type="range" id="brightness" min="0" max="100" value="50">
        <span id="brightnessValue" style="color: white;">50</span>
      </div>
      
      <div class="setting-group">
        <label>Rotation:</label>
        <select id="rotation">
          <option value="0">0°</option>
          <option value="90">90°</option>
          <option value="180">180°</option>
          <option value="270">270°</option>
        </select>
      </div>
      
      <button onclick="applySettings()">✅ Appliquer</button>
    </div>
  </div>
  
  <script src="camera-stream.js"></script>
</body>
</html>
```

#### JavaScript (camera-stream.js)

```javascript
class CameraStream {
  constructor() {
    this.robotIP = document.getElementById('robotIP').value;
    this.streamElement = document.getElementById('stream');
    this.overlayElement = document.getElementById('overlay');
    
    this.init();
    this.bindEvents();
  }
  
  init() {
    this.updateStreamUrl();
    
    // Handle image load
    this.streamElement.addEventListener('load', () => {
      this.overlayElement.style.display = 'none';
    });
    
    // Handle image error
    this.streamElement.addEventListener('error', () => {
      this.overlayElement.style.display = 'flex';
      this.overlayElement.textContent = '❌ Erreur de connexion';
    });
  }
  
  updateStreamUrl() {
    const url = `http://${this.robotIP}:8000/api/camera/stream?t=${Date.now()}`;
    this.streamElement.src = url;
    this.overlayElement.style.display = 'flex';
    this.overlayElement.textContent = 'Chargement du flux...';
  }
  
  bindEvents() {
    // Snapshot button
    document.getElementById('snapshot').addEventListener('click', () => {
      this.takeSnapshot();
    });
    
    // Fullscreen button
    document.getElementById('fullscreen').addEventListener('click', () => {
      this.toggleFullscreen();
    });
    
    // Reconnect button
    document.getElementById('reconnect').addEventListener('click', () => {
      this.robotIP = document.getElementById('robotIP').value;
      this.updateStreamUrl();
    });
    
    // Brightness slider
    document.getElementById('brightness').addEventListener('input', (e) => {
      document.getElementById('brightnessValue').textContent = e.target.value;
    });
  }
  
  async takeSnapshot() {
    try {
      const response = await fetch(
        `http://${this.robotIP}:8000/api/camera/snapshot`
      );
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `tachikoma-${Date.now()}.jpg`;
      a.click();
      
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Snapshot failed:', error);
      alert('Échec de la capture');
    }
  }
  
  toggleFullscreen() {
    const container = this.streamElement.parentElement;
    
    if (!document.fullscreenElement) {
      container.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }
}

// Apply camera settings
async function applySettings() {
  const robotIP = document.getElementById('robotIP').value;
  const brightness = parseInt(document.getElementById('brightness').value);
  const rotation = parseInt(document.getElementById('rotation').value);
  
  try {
    const response = await fetch(
      `http://${robotIP}:8000/api/camera/settings`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          brightness,
          rotation
        })
      }
    );
    
    if (response.ok) {
      alert('✅ Paramètres appliqués');
      // Reconnect stream
      camera.updateStreamUrl();
    } else {
      alert('❌ Erreur lors de l\'application des paramètres');
    }
  } catch (error) {
    console.error('Settings update failed:', error);
    alert('❌ Erreur de connexion');
  }
}

// Initialize
const camera = new CameraStream();
```

---

## 🔧 Configuration et Optimisation

### Résolutions Recommandées

| Résolution | Usage | FPS | Latence | Bande passante |
|------------|-------|-----|---------|----------------|
| **320x240** | Monitoring léger | 30 | ~100ms | ~0.5 Mb/s |
| **640x480** | Usage standard | 30 | ~150ms | ~1.5 Mb/s |
| **1280x720** | HD | 15-20 | ~250ms | ~3 Mb/s |
| **1920x1080** | Full HD | 10-15 | ~400ms | ~5 Mb/s |

### Paramètres de Qualité

```javascript
const cameraSettings = {
  // Résolution
  resolution: [640, 480],  // Balance qualité/performance
  
  // Framerate
  framerate: 30,  // 15-30 FPS recommandé
  
  // Qualité JPEG (0-100)
  quality: 85,  // 85 = bon compromis
  
  // Rotation
  rotation: 0,  // 0, 90, 180, 270
  
  // Luminosité (-100 à 100)
  brightness: 0,
  
  // Contraste (-100 à 100)
  contrast: 0,
  
  // Saturation (-100 à 100)
  saturation: 0
};
```

---

## ⚡ Optimisation des Performances

### 1. Réduire la Latence

```javascript
// Désactiver le cache du navigateur
const streamUrl = `http://${robotIP}:8000/api/camera/stream?nocache=${Date.now()}`;

// Utiliser fetch avec keepalive
const response = await fetch(streamUrl, {
  cache: 'no-store',
  keepalive: true
});
```

### 2. Adaptive Streaming

```javascript
class AdaptiveStream {
  constructor(robotIP) {
    this.robotIP = robotIP;
    this.connectionQuality = 'good';
    this.resolutions = {
      low: [320, 240],
      medium: [640, 480],
      high: [1280, 720]
    };
  }
  
  async adjustQuality() {
    // Mesurer la latence
    const start = Date.now();
    await fetch(`http://${this.robotIP}:8000/api/health`);
    const latency = Date.now() - start;
    
    // Adapter la résolution
    if (latency > 500) {
      this.connectionQuality = 'poor';
      await this.setResolution(this.resolutions.low);
    } else if (latency > 200) {
      this.connectionQuality = 'medium';
      await this.setResolution(this.resolutions.medium);
    } else {
      this.connectionQuality = 'good';
      await this.setResolution(this.resolutions.high);
    }
  }
  
  async setResolution(resolution) {
    await fetch(`http://${this.robotIP}:8000/api/camera/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolution })
    });
  }
}
```

### 3. Buffering et Préchargement

```javascript
class BufferedStream {
  constructor(robotIP) {
    this.robotIP = robotIP;
    this.buffer = [];
    this.bufferSize = 3;
  }
  
  async preloadFrames() {
    while (this.buffer.length < this.bufferSize) {
      const response = await fetch(
        `http://${this.robotIP}:8000/api/camera/snapshot`
      );
      const blob = await response.blob();
      this.buffer.push(URL.createObjectURL(blob));
    }
  }
  
  getNextFrame() {
    if (this.buffer.length > 0) {
      return this.buffer.shift();
    }
    return null;
  }
}
```

---

## 🌐 WebSocket pour Contrôle en Temps Réel

### Intégration WebSocket + Vidéo

```javascript
class RobotController {
  constructor(robotIP) {
    this.robotIP = robotIP;
    this.ws = null;
    this.initWebSocket();
  }
  
  initWebSocket() {
    this.ws = new WebSocket(`ws://${this.robotIP}:8000/ws`);
    
    this.ws.onopen = () => {
      console.log('✅ WebSocket connecté');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleRobotData(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };
  }
  
  handleRobotData(data) {
    // Mettre à jour les infos de télémétrie
    if (data.type === 'telemetry') {
      document.getElementById('battery').textContent = 
        `${data.battery}%`;
      document.getElementById('distance').textContent = 
        `${data.ultrasonic}cm`;
    }
  }
  
  sendCommand(command) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(command));
    }
  }
  
  // Contrôle clavier
  enableKeyboardControl() {
    document.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'ArrowUp':
          this.sendCommand({ action: 'move', direction: 'forward' });
          break;
        case 'ArrowDown':
          this.sendCommand({ action: 'move', direction: 'backward' });
          break;
        case 'ArrowLeft':
          this.sendCommand({ action: 'turn', direction: 'left' });
          break;
        case 'ArrowRight':
          this.sendCommand({ action: 'turn', direction: 'right' });
          break;
        case ' ':
          this.sendCommand({ action: 'stop' });
          break;
      }
    });
  }
}

// Utilisation
const robot = new RobotController('192.168.1.100');
robot.enableKeyboardControl();
```

---

## 📊 Affichage de Télémétrie Overlay

### Overlay sur la vidéo

```jsx
const VideoWithTelemetry = ({ robotIP }) => {
  const [telemetry, setTelemetry] = useState({
    battery: 0,
    distance: 0,
    temperature: 0
  });
  
  useEffect(() => {
    const ws = new WebSocket(`ws://${robotIP}:8000/ws`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'telemetry') {
        setTelemetry(data);
      }
    };
    
    return () => ws.close();
  }, [robotIP]);
  
  return (
    <div className="video-with-overlay">
      <img src={`http://${robotIP}:8000/api/camera/stream`} />
      
      <div className="telemetry-overlay">
        <div className="stat">
          <span className="icon">🔋</span>
          <span className="value">{telemetry.battery}%</span>
        </div>
        <div className="stat">
          <span className="icon">📏</span>
          <span className="value">{telemetry.distance}cm</span>
        </div>
        <div className="stat">
          <span className="icon">🌡️</span>
          <span className="value">{telemetry.temperature}°C</span>
        </div>
      </div>
    </div>
  );
};
```

```css
.video-with-overlay {
  position: relative;
}

.telemetry-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  padding: 10px;
  border-radius: 8px;
  color: white;
  font-family: monospace;
}

.stat {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.stat .value {
  font-weight: bold;
}
```

---

## 🐛 Troubleshooting

### Problème: Pas d'image

**Vérifications:**

1. **Connectivité réseau:**
```bash
ping 192.168.1.100
```

2. **Service API actif:**
```bash
ssh feiyu@192.168.1.100
sudo systemctl status tachikoma-api
```

3. **Caméra détectée:**
```bash
vcgencmd get_camera
# Doit retourner: supported=1 detected=1
```

4. **Tester l'endpoint:**
```bash
curl http://192.168.1.100:8000/api/camera/snapshot -o test.jpg
```

---

### Problème: Latence élevée

**Solutions:**

1. **Réduire la résolution:**
```javascript
await updateSettings({ resolution: [320, 240] });
```

2. **Diminuer le framerate:**
```javascript
await updateSettings({ framerate: 15 });
```

3. **Réduire la qualité JPEG:**
```javascript
await updateSettings({ quality: 70 });
```

4. **Vérifier le WiFi:**
```bash
iwconfig wlan0
# Vérifier Link Quality et Signal level
```

---

### Problème: Image saccadée

**Causes possibles:**

1. **Bande passante insuffisante** → Réduire résolution/qualité
2. **CPU du Raspberry Pi surchargé** → Fermer d'autres services
3. **Trop de connexions simultanées** → Limiter à 1-2 viewers

---

## 🔐 Sécurité

### HTTPS et Authentification

**Configuration Nginx avec SSL:**

```nginx
server {
    listen 443 ssl;
    server_name tachikoma.local;
    
    ssl_certificate /etc/ssl/certs/tachikoma.crt;
    ssl_certificate_key /etc/ssl/private/tachikoma.key;
    
    location /api/camera/stream {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        
        # Authentification basique
        auth_basic "Tachikoma Camera";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

**Client avec authentification:**

```javascript
const streamUrl = 'https://user:password@tachikoma.local/api/camera/stream';
```

---

## 📱 Support Mobile

### Responsive Design

```css
@media (max-width: 768px) {
  .video-container {
    max-width: 100vw;
    height: auto;
  }
  
  .controls {
    flex-direction: column;
  }
  
  .controls button {
    width: 100%;
  }
}
```

### Touch Controls

```javascript
const touchControls = {
  init(element) {
    let touchStartY = 0;
    
    element.addEventListener('touchstart', (e) => {
      touchStartY = e.touches[0].clientY;
    });
    
    element.addEventListener('touchmove', (e) => {
      const touchY = e.touches[0].clientY;
      const deltaY = touchY - touchStartY;
      
      if (Math.abs(deltaY) > 50) {
        if (deltaY < 0) {
          // Swipe up - zoom in
          this.zoom(1.1);
        } else {
          // Swipe down - zoom out
          this.zoom(0.9);
        }
        touchStartY = touchY;
      }
    });
  },
  
  zoom(factor) {
    const img = document.getElementById('stream');
    const currentScale = parseFloat(img.style.transform.match(/scale\(([^)]+)\)/)?.[1] || 1);
    const newScale = Math.max(1, Math.min(3, currentScale * factor));
    img.style.transform = `scale(${newScale})`;
  }
};

touchControls.init(document.querySelector('.video-container'));
```

---

## 🎯 Exemples Complets

### Dashboard Complet React

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RobotDashboard = () => {
  const robotIP = '192.168.1.100';
  const [telemetry, setTelemetry] = useState({});
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    const ws = new WebSocket(`ws://${robotIP}:8000/ws`);
    
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => setTelemetry(JSON.parse(e.data));
    
    return () => ws.close();
  }, []);
  
  const sendCommand = async (endpoint) => {
    await axios.post(`http://${robotIP}:8000/api/${endpoint}`);
  };
  
  return (
    <div className="dashboard">
      <header>
        <h1>🤖 Tachikoma Control Center</h1>
        <div className={`status ${connected ? 'connected' : 'disconnected'}`}>
          {connected ? '✅ Connecté' : '❌ Déconnecté'}
        </div>
      </header>
      
      <main>
        <div className="video-section">
          <img 
            src={`http://${robotIP}:8000/api/camera/stream`}
            alt="Robot Camera"
          />
          <div className="telemetry">
            <div>🔋 {telemetry.battery}%</div>
            <div>📏 {telemetry.distance}cm</div>
            <div>🌡️ {telemetry.temp}°C</div>
          </div>
        </div>
        
        <div className="controls-section">
          <button onClick={() => sendCommand('movement/forward')}>⬆️</button>
          <button onClick={() => sendCommand('movement/left')}>⬅️</button>
          <button onClick={() => sendCommand('movement/stop')}>⏹️</button>
          <button onClick={() => sendCommand('movement/right')}>➡️</button>
          <button onClick={() => sendCommand('movement/backward')}>⬇️</button>
        </div>
      </main>
    </div>
  );
};

export default RobotDashboard;
```

---

## 📚 Ressources Complémentaires

- [API Complète du Robot](../api/README.md)
- [Configuration Raspberry Pi Camera](../hardware/camera.md)
- [WebSocket Protocol](../api/websocket.md)
- [Sécurité et Authentification](../security/authentication.md)

---

## 💡 Bonnes Pratiques

✅ **À Faire:**
- Gérer les erreurs de connexion gracieusement
- Implémenter un système de reconnexion automatique
- Afficher un indicateur de chargement
- Adapter la qualité selon la bande passante
- Utiliser HTTPS en production

❌ **À Éviter:**
- Ouvrir plusieurs connexions simultanées au stream
- Utiliser une résolution trop élevée sur réseau faible
- Oublier de gérer les timeouts
- Ignorer les erreurs réseau
- Bloquer l'UI pendant le chargement

---

**Dernière mise à jour:** 15 janvier 2026
