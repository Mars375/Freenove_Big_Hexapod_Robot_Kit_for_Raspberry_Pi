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
  - `Code/Server/servo.py` - Contrôle servos
  - `Code/Server/control.py` - Logique mouvement
  - `Code/Server/point.txt` - Calibration
  - `Code/Server/parameter.py` - Gestion config
