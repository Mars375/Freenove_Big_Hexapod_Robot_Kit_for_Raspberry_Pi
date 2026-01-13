# 🔍 Analyse complète du repo Freenove - Hardware Bridge Refactoring

**Date**: 2026-01-13  
**Objectif**: Garantir la compatibilité 100% entre notre architecture HAL moderne et le robot physique Freenove

---

## 📊 Vue d'ensemble de l'architecture Freenove

### Structure hardware
```
Freenove Hexapod Robot:
├── 2x PCA9685 (0x40, 0x41) - 32 canaux PWM
├── 1x MPU6050 (0x68) - IMU 6-axis
├── 1x ADS7830 (0x4b) - ADC 8-channel
├── 18 servos (6 pattes × 3 servos)
└── LED RGB, buzzer, ultrasonic, camera
```

### Mapping des servos (CRITIQUE)

#### PCA9685 - Adresse 0x41 (canaux 0-15)
- **Patte 1** (avant droite): Canaux 15, 14, 13 (coxa, femur, tibia)
- **Patte 2** (milieu droite): Canaux 12, 11, 10
- **Patte 3** (arrière droite): Canaux 9, 8, 31*

#### PCA9685 - Adresse 0x40 (canaux 16-31)
- **Patte 6** (avant gauche): Canaux 16, 17, 18
- **Patte 5** (milieu gauche): Canaux 19, 20, 21
- **Patte 4** (arrière gauche): Canaux 22, 23, 27*

> ⚠️ **Note**: Les canaux 31 et 27 sont des cas spéciaux (tibia pattes 3 et 4)

---

## 🎯 Configuration PWM des servos

### Formule de conversion angle → PWM
```python
# Étape 1: Angle (0-180°) → Pulse width (µs)
dutycycle_us = map_value(angle, 0, 180, 500, 2500)

# Étape 2: Pulse width → Valeur 12-bit pour PCA9685
dutycycle_12bit = map_value(dutycycle_us, 0, 20000, 0, 4095)
```

### Valeurs PWM clés
| Angle | Pulse Width (µs) | Valeur 12-bit |
|-------|------------------|---------------|
| 0°    | 500              | ~122          |
| 90°   | 1500             | ~307          |
| 180°  | 2500             | ~512          |

**Fréquence PWM**: 50 Hz (période 20ms)

---

## 🦿 Géométrie et cinématique inverse

### Dimensions des segments (en mm)
- **l1** (coxa): 33 mm
- **l2** (femur): 90 mm
- **l3** (tibia): 110 mm
- **Longueur totale patte**: 233 mm (max étendue)

### Limites de travail
- **Min**: 90 mm (patte repliée)
- **Max**: 248 mm (patte étendue)
- **Hauteur corps par défaut**: -25 mm

### Positions de calibration (point.txt)
```
Patte 1: [140, 0, 0]
Patte 2: [140, 0, 0]
Patte 3: [140, 0, 0]
Patte 4: [140, 0, 0]
Patte 5: [140, 0, 0]
Patte 6: [140, 0, 0]
```
**Format**: `[x, y, z]` en coordonnées cylindriques relatives

---

## 🔄 Transformation angulaire

### Pattes droites (1, 2, 3)
```python
servo_angle_coxa = current_angle[0] + calibration[0]
servo_angle_femur = 90 - (current_angle[1] + calibration[1])
servo_angle_tibia = current_angle[2] + calibration[2]
```

### Pattes gauches (4, 5, 6)
```python
servo_angle_coxa = current_angle[0] + calibration[0]
servo_angle_femur = 90 + current_angle[1] + calibration[1]
servo_angle_tibia = 180 - (current_angle[2] + calibration[2])
```

> 💡 **Raison**: Les servos des pattes gauches sont montés en miroir

---

## 🎮 Angles spéciaux de montage

Dans le test de calibration (`servo.py` main), Freenove utilise:
```python
for i in range(32):
    if i in [10, 13, 31]:  # Tibias pattes 2, 1, 3
        servo.set_servo_angle(i, 10)  # Angle minimum
    elif i in [18, 21, 27]:  # Tibias pattes 6, 5, 4
        servo.set_servo_angle(i, 170)  # Angle maximum
    else:
        servo.set_servo_angle(i, 90)  # Position neutre
```

**Interprétation**: Compense le montage physique asymétrique des tibias

---

## 📐 Points d'attache des pattes (body_points)

En coordonnées cartésiennes (mm):
```python
body_points = [
    [137.1, 189.4, body_height],   # Patte 1 (avant droite)
    [225, 0, body_height],          # Patte 2 (milieu droite)
    [137.1, -189.4, body_height],   # Patte 3 (arrière droite)
    [-137.1, -189.4, body_height],  # Patte 4 (arrière gauche)
    [-225, 0, body_height],         # Patte 5 (milieu gauche)
    [-137.1, 189.4, body_height]    # Patte 6 (avant gauche)
]
```

Angles de rotation pour transformation:
- Patte 1: 54°
- Patte 2: 0°
- Patte 3: -54°
- Patte 4: -126°
- Patte 5: 180°
- Patte 6: 126°

---

## 🚶 Gaits (Allures de marche)

### Gait 1: Tripod (rapide)
- **Groupes alternés**: [0,2,4] et [1,3,5]
- **Cycle**: 8 phases
- **Vitesse**: F = map(speed, 2-10, 126-22)

### Gait 2: Wave (stable)
- **Séquence**: [5,2,1,0,3,4] (une patte à la fois)
- **Cycle**: 6 phases × F/6 steps
- **Vitesse**: F = map(speed, 2-10, 171-45)

---

## 🔧 Notre architecture HAL vs Freenove

### ✅ Points de compatibilité

| Composant | Freenove | Notre HAL | Compatible |
|-----------|----------|-----------|------------|
| **Interface I2C** | smbus direct | `I2CInterface` | ✅ Oui |
| **PCA9685** | Adafruit lib | `PCA9685` driver | ✅ Oui |
| **MPU6050** | smbus direct | `MPU6050` driver | ✅ Oui |
| **ADS7830** | smbus direct | `ADS7830` driver | ✅ Oui |
| **Servo Controller** | Classe `Servo` | `ServoController` | ✅ Oui |

### 🔄 Adaptations nécessaires

#### 1. Mapping des canaux servos
**Notre HAL** doit implémenter le même mapping que Freenove:
```python
SERVO_CHANNEL_MAP = {
    # Patte 1
    (0, 'coxa'): 15,
    (0, 'femur'): 14,
    (0, 'tibia'): 13,
    # ... etc
}
```

#### 2. Transformation angulaire
Intégrer les corrections de montage:
- Pattes droites: femur inversé (90 - angle)
- Pattes gauches: tibia inversé (180 - angle)

#### 3. Calibration
Charger/sauvegarder le fichier `point.txt` pour persister la calibration

---

## 🎯 Checklist pour tests hardware réels

### Phase 1: Validation basique
- [ ] Test I2C scan (détecter 0x40, 0x41, 0x68, 0x4b)
- [ ] Test PCA9685 initialisation (50 Hz)
- [ ] Test servo individuel (canal par canal)
- [ ] Vérifier angles min/max (0° = 500µs, 180° = 2500µs)

### Phase 2: Calibration
- [ ] Position neutre (tous servos à 90°)
- [ ] Position test Freenove ([10,13,31]→10°, [18,21,27]→170°)
- [ ] Ajuster calibration si nécessaire
- [ ] Sauvegarder dans `point.txt`

### Phase 3: Cinématique
- [ ] Test cinématique inverse (coord → angles)
- [ ] Test transformation de repère (body → leg)
- [ ] Validation limites (90-248mm)

### Phase 4: Mouvements
- [ ] Position home (toutes pattes à [140,0,0])
- [ ] Tripod gait (marche avant)
- [ ] Contrôle IMU (stabilisation)

---

## 📋 Différences clés à implémenter

### 1. Dual PCA9685
```python
# Freenove utilise 2 contrôleurs
self.pwm_40 = PCA9685(0x40)  # Canaux 16-31
self.pwm_41 = PCA9685(0x41)  # Canaux 0-15

# Logique de routage
if channel < 16:
    self.pwm_41.set_pwm(channel, 0, dutycycle)
else:
    channel -= 16
    self.pwm_40.set_pwm(channel, 0, dutycycle)
```

### 2. Relax mode
```python
def relax():
    """Désactive tous les servos (économie d'énergie)"""
    for i in range(8):
        self.pwm_41.set_pwm(i + 8, 4096, 4096)
        self.pwm_40.set_pwm(i, 4096, 4096)
        self.pwm_40.set_pwm(i + 8, 4096, 4096)
```
Valeur 4096 = OFF pour PCA9685

### 3. GPIO Power Control
```python
from gpiozero import OutputDevice
servo_power_disable = OutputDevice(4)
servo_power_disable.off()  # Enable servos
```
GPIO 4 contrôle l'alimentation des servos

---

## 🚀 Script de test recommandé

Voir `tests/hardware/test_real_hexapod.py` (à créer)

---

## 📚 Références

- [Freenove Original Repo](https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi)
- Fichiers clés analysés:
- 
---

## 🧠 Modules supplémentaires analysés

### 🎯 Filtre de Kalman (kalman.py)

**Classe**: `Kalman_filter`

**Paramètres d'initialisation**:
- `process_noise_covariance` (Q): Covariance du bruit du processus
- `measurement_noise_covariance` (R): Covariance du bruit de mesure

**Implémentation**: Filtre de Kalman 1D standard pour stabiliser les lectures ADC de l'IMU

```python
kalman_filter = Kalman_filter(0.001, 0.1)  # Valeurs typiques
```

**Particularités**:
- Gestion des changements brusques: si `|valeur_precedente - valeur_actuelle| >= 60`, utilise moyenne pondérée (40% nouvelle / 60% ancienne)
- Sinon, utilise l'équation complète du filtre de Kalman

**✅ Notre implémentation**: À intégrer dans `drivers/imu.py` pour la stabilisation des lectures

---

### 💡 Contrôle LED (led.py)

**Classe**: `Led`

**Compatibilité matérielle**:
- **PCB v1.0 + Pi 1-4**: WS281X (rpi_ledpixel) - 7 LEDs, GPIO PWM, format RGB
- **PCB v2.0 + Pi 1-5**: SPI LedPixel (spi_ledpixel) - 7 LEDs, format GRB
- **PCB v1.0 + Pi 5**: Non supporté (erreur)

**Modes LED**: 
- `0`: Off
- `1`: Couleur fixe (led_index avec masque 0x7f)
- `2`: Color wipe (rouge/vert/bleu)
- `3`: Theater chase
- `4`: Rainbow
- `5`: Rainbow cycle

**Commande**: `process_light_command(data)` avec format: `['CMD', mode, R, G, B]`

**✅ Notre implémentation**: Compatible via notre abstraction HAL, à implémenter dans `drivers/led.py`

---

### 🔊 Buzzer (buzzer.py)

**Classe**: `Buzzer`

**Configuration**:
- GPIO Pin: **17**
- Bibliothèque: `gpiozero.OutputDevice`

**Méthodes**:
- `set_state(bool)`: Active/désactive le buzzer
- `close()`: Libère les ressources GPIO

**✅ Notre implémentation**: Simple à intégrer dans `drivers/buzzer.py` avec l'abstraction GPIO

---

### 🎥 Caméra (camera.py)

**Classe**: `Camera`

**Bibliothèque**: `picamera2` (Pi 5 compatible)

**Fonctionnalités**:
1. **Preview**: Capture d'images avec QTGL preview
2. **Streaming**: JPEG encoder via `StreamingOutput` avec threading.Condition
3. **Recording**: H264 encoder vers fichier

**Configuration par défaut**:
- Preview size: 640x480
- Stream size: 400x300
- Transform: hflip/vflip supporté

**Streaming architecture**:
```python
class StreamingOutput(io.BufferedIOBase):
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
```

**✅ Notre implémentation**: À ajouter dans `drivers/camera.py` pour vision et téléopération

---

### 🧵 Gestion des Threads (Thread.py)

**Fonction**: `stop_thread(thread)`

**Implémentation**: Utilise `ctypes.pythonapi.PyThreadState_SetAsyncExc` pour arrêter les threads

**Mécanisme**: 
- Lève une exception `SystemExit` dans le thread cible
- Réessaie 5 fois pour s'assurer de l'arrêt

**⚠️ Note**: Méthode dangereuse (force kill), à utiliser avec précaution

**✅ Notre implémentation**: Utiliser `threading.Event` plus sûr dans notre architecture moderne

---

### 🏛️ Architecture principale (main.py)

**Classe**: `MyWindow(QMainWindow, Ui_server)`

**Stack technique**:
- **Interface**: PyQt5 (QApplication, QMainWindow)
- **Serveur**: TCP socket (video + commands)
- **Threading**: 2 threads principaux
  - `video`: Transmission vidéo continue
  - `instruction`: Réception commandes

**Modes de lancement**:
- `-t`: Start TCP server automatically
- `-n`: Mode sans UI (headless)

**Gestion arrêt**:
```python
def closeEvent(self, event):
    Thread.stop_thread(self.video)
    Thread.stop_thread(self.instruction)
    self.server.stop_server()
```

**✅ Notre implémentation**: Architecture moderne avec FastAPI + WebSockets déjà en place

---



## 🔬 Comparaison détaillée des drivers

### 1. ADC (ADS7830)

#### Freenove `adc.py`
```python
class ADC:
    def __init__(self):
        self.ADS7830_COMMAND = 0x84
        self.adc_voltage_coefficient = 3  # PCB v3.0
        self.i2c_bus = smbus.SMBus(1)  # Direct smbus
        self.I2C_ADDRESS = 0x48
    
    def read_channel_voltage(self, channel: int) -> float:
        command_set = self.ADS7830_COMMAND | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
        self.i2c_bus.write_byte(self.I2C_ADDRESS, command_set)
        value = self._read_stable_byte()
        voltage = value / 255.0 * 5 * self.adc_voltage_coefficient
        return round(voltage, 2)
```

#### Notre HAL `drivers/adc.py`
```python
class ADS7830(IHardwareComponent):
    def __init__(self, i2c_interface: I2CInterface, address: int = 0x4b):
        self._i2c = i2c_interface  # Interface HAL
        self._address = address
        self.COMMAND_BYTE = 0x84
        self.REFERENCE_VOLTAGE = 3.3
    
    async def read_channel(self, channel: int) -> int:
        command = self.COMMAND_BYTE | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
        await self._i2c.write_byte(self._address, command)
        return await self._i2c.read_byte(self._address)
    
    async def read_voltage(self, channel: int) -> float:
        value = await self.read_channel(channel)
        return (value / 255.0) * self.REFERENCE_VOLTAGE
```

**Différences clés**:
- ✅ **Même algorithme** de conversion canal
- ⚠️ **Adresse**: Freenove utilise `0x48`, nous `0x4b` (vérifier hardware)
- ⚠️ **Coefficient**: Freenove `×3` pour tension batterie, nous `×1` (vérifier PCB version)
- ✅ **Interface**: Notre HAL abstrait smbus via I2CInterface
- ✅ **Async**: Notre implémentation est async-ready

**Action requise**: 
- Ajouter paramètre `voltage_coefficient` optionnel
- Vérifier adresse I2C sur hardware réel

---

### 2. IMU (MPU6050)

#### Freenove `imu.py`
```python
class IMU:
    def __init__(self):
        self.sensor = mpu6050(address=0x68, bus=1)  # Lib mpu6050
        self.sensor.set_accel_range(mpu6050.ACCEL_RANGE_2G)
        self.sensor.set_gyro_range(mpu6050.GYRO_RANGE_250DEG)
        
        # Filtre Kalman pour chaque axe
        self.kalman_filter_AX = Kalman_filter(0.001, 0.1)
        self.kalman_filter_AY = Kalman_filter(0.001, 0.1)
        # ...
        
        # Quaternions pour fusion IMU
        self.quaternion_w = 1
        self.quaternion_x = 0
        # ...
        
        # Calibration automatique (100 échantillons)
        self.error_accel_data, self.error_gyro_data = self.calculate_average_sensor_data()
    
    def update_imu_state(self):
        # Lecture + Kalman + Fusion quaternion
        # Retourne pitch, roll, yaw en degrés
        return self.pitch_angle, self.roll_angle, self.yaw_angle
```

#### Notre HAL `drivers/imu.py`
```python
class MPU6050(IHardwareComponent):
    def __init__(self, i2c_interface: I2CInterface, address: int = 0x68):
        self._i2c = i2c_interface
        self._address = address
    
    async def initialize(self) -> None:
        # Wake up MPU6050
        await self._i2c.write_byte_data(self._address, self.PWR_MGMT_1, 0x00)
        await asyncio.sleep(0.1)
    
    async def read_accelerometer(self) -> Tuple[float, float, float]:
        data = await self._i2c.read_i2c_block_data(self._address, self.ACCEL_XOUT_H, 6)
        # Conversion raw → m/s²
        return (ax, ay, az)
    
    async def read_gyroscope(self) -> Tuple[float, float, float]:
        data = await self._i2c.read_i2c_block_data(self._address, self.GYRO_XOUT_H, 6)
        # Conversion raw → °/s
        return (gx, gy, gz)
```

**Différences critiques**:
- ❌ **Filtre Kalman**: Freenove l'implémente, nous **NON**
- ❌ **Fusion quaternion**: Freenove calcule pitch/roll/yaw, nous **NON**
- ❌ **Calibration auto**: Freenove fait 100 mesures au démarrage, nous **NON**
- ✅ **Lecture brute**: Compatible, mêmes registres

**Action requise (URGENT)**:
1. Ajouter classe `KalmanFilter` dans notre HAL
2. Ajouter fusion quaternion (ou utiliser lib existante)
3. Ajouter méthode `calibrate()` avec moyenne 100 échantillons
4. Ajouter méthode `get_orientation()` → (pitch, roll, yaw)

**Freenove utilise**:
- Proportional gain: 100
- Integral gain: 0.002
- Half time step: 0.001

---

### 3. PCA9685

#### Freenove `pca9685.py`
```python
class PCA9685:
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    # ...
    
    def __init__(self, address: int = 0x40, debug: bool = False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.write(self.__MODE1, 0x00)
    
    def set_pwm_freq(self, freq: float) -> None:
        prescaleval = 25000000.0 / 4096.0 / float(freq) - 1.0
        prescale = math.floor(prescaleval + 0.5)
        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # Sleep
        self.write(self.__MODE1, newmode)
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
    
    def set_pwm(self, channel: int, on: int, off: int) -> None:
        self.write(self.__LED0_ON_L + 4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4*channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4*channel, off >> 8)
```

#### Notre HAL `drivers/pca9685.py`
```python
class PCA9685(IHardwareComponent):
    def __init__(self, i2c_interface: I2CInterface, address: int = 0x40):
        self._i2c = i2c_interface
        self._address = address
        # Mêmes registres
    
    async def initialize(self, frequency: int = 50) -> None:
        await self._i2c.write_byte_data(self._address, self.MODE1, 0x00)
        await asyncio.sleep(0.01)
        await self.set_pwm_freq(frequency)
    
    async def set_pwm_freq(self, freq: int) -> None:
        # IDENTIQUE à Freenove
        prescale = int(25000000.0 / 4096.0 / freq - 1)
        # ...
    
    async def set_pwm(self, channel: int, on: int, off: int) -> None:
        # IDENTIQUE à Freenove
```

**Compatibilité**: ✅ **100% compatible**
- Même algorithme de fréquence
- Mêmes registres
- Même formule prescale

---

### 4. PID Controller

#### Freenove `pid.py`
```python
class Incremental_PID:
    def __init__(self, P=0.0, I=0.0, D=0.0):
        self.kp = P
        self.ki = I
        self.kd = D
        self.last_error = 0.0
        self.i_error = 0.0
        self.i_saturation = 10.0  # Anti-windup
    
    def pid_calculate(self, feedback_val):
        error = self.target_value - feedback_val
        self.p_error = self.kp * error
        self.i_error += error
        self.d_error = self.kd * (error - self.last_error)
        
        # Anti-windup
        if self.i_error < -self.i_saturation:
            self.i_error = -self.i_saturation
        elif self.i_error > self.i_saturation:
            self.i_error = self.i_saturation
        
        self.output = self.p_error + (self.ki * self.i_error) + self.d_error
        self.last_error = error
        return self.output
```

**Notre HAL**: ❌ **Pas implémenté**

**Action requise**:
- Créer `core/hardware/controllers/pid_controller.py`
- Implémenter PID incrémental avec anti-windup
- Utiliser pour stabilisation IMU (control.py utilise PID avec kp=0.5, ki=0.0, kd=0.0025)

---

## 🛠️ Résumé des adaptations nécessaires

### ✅ Compatible (prêt pour tests)
1. **PCA9685**: 100% compatible
2. **Structure I2C**: Notre abstraction fonctionne

### ⚠️ Nécessite ajustements mineurs
3. **ADS7830**: 
   - Ajouter param `voltage_coefficient`
   - Vérifier adresse (0x48 vs 0x4b)

### 🚨 Nécessite implémentation complète
4. **MPU6050**: 
   - ❌ Filtre Kalman (6 axes)
   - ❌ Fusion quaternion
   - ❌ Calibration automatique
   - ❌ Méthode `get_orientation()`

5. **PID Controller**:
   - ❌ Classe `Incremental_PID`
   - ❌ Anti-windup

---

## 🎯 Plan d'action pour tests hardware

### Phase 1: Tests basiques (✅ Prêt)
- [ ] I2C scan
- [ ] PCA9685 init + set_pwm
- [ ] Servos individuels
- [ ] ADC lecture tension

### Phase 2: IMU (besoin travail)
- [ ] Implémenter KalmanFilter
- [ ] Implémenter fusion quaternion
- [ ] Implémenter calibration
- [ ] Tester orientation

### Phase 3: Mouvement complet
- [ ] Implémenter PID
- [ ] Intégrer dans controllers
- [ ] Test stabilisation
- [ ] Test gaits

---

**Priorité immédiate**: Implémenter IMU complet (Kalman + quaternion) car utilisé pour stabilisation
  - `Code/Server/servo.py` - Contrôle servos
  - `Code/Server/control.py` - Logique mouvement
  - `Code/Server/point.txt` - Calibration
  - `Code/Server/parameter.py` - Gestion config
