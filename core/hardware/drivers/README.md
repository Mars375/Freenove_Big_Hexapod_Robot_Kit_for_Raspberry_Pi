# Drivers Hardware HAL

Ce dossier contient tous les drivers hardware modernisés utilisant l'architecture HAL (Hardware Abstraction Layer).

## Architecture

```
Hardware Factory
    ↓
I2CInterface (HAL bas niveau)
    ↓
Drivers de Base
├── PCA9685 (Contrôleur PWM)
├── ADC (Convertisseur Analogique-Numérique)
└── MPU6050 (IMU: Accéléromètre + Gyroscope)
    ↓
Contrôleurs Haut Niveau
└── PCA9685ServoController
```

## Drivers Disponibles

### 1. PCA9685 (pca9685.py)

**Contrôleur PWM 16 canaux pour servomoteurs**

```python
from core.hardware.factory import get_hardware_factory

# Via la factory (recommandé)
factory = get_hardware_factory()
pca9685 = await factory.get_pca9685(address=0x40, frequency=50)

# Configuration PWM
await pca9685.set_pwm(channel=0, on=0, off=2048)
await pca9685.set_servo_pulse(channel=0, pulse=1500)  # 1500µs

# Configuration multiple
await pca9685.set_all_pwm(on=0, off=0)  # Éteindre tous

# Cleanup
await pca9685.cleanup()
```

**Caractéristiques:**
- 16 canaux PWM (0-15)
- Fréquence configurable (défaut 50Hz pour servos)
- Adresse I2C par défaut: 0x40
- Async pour toutes opérations I2C
- Interface IHardwareComponent

### 2. ADC (adc.py)

**Convertisseur Analogique-Numérique ADS7830**

```python
# Via la factory
factory = get_hardware_factory()
adc = await factory.get_adc(address=0x48)

# Lecture d'un canal (retourne tension en V)
voltage = await adc.read_channel(0)  # Canal 0
print(f"Tension: {voltage:.2f}V")

# Lecture de tous les canaux
voltages = await adc.read_all_channels()
for i, v in enumerate(voltages):
    print(f"Canal {i}: {v:.2f}V")

# Cleanup
await adc.cleanup()
```

**Caractéristiques:**
- 4 canaux analogiques (0-3)
- Résolution 12-bit (0-4095)
- Tension de référence: 3.3V
- Adresse I2C par défaut: 0x48
- Retourne valeurs en volts

### 3. MPU6050 (imu.py)

**IMU 6-axis: Accéléromètre + Gyroscope**

```python
# Via la factory
factory = get_hardware_factory()
imu = await factory.get_imu(address=0x68)

# Lecture accéléromètre (en g)
accel = await imu.read_accelerometer()
print(f"Accélération: X={accel[0]:.2f}g Y={accel[1]:.2f}g Z={accel[2]:.2f}g")

# Lecture gyroscope (en deg/s)
gyro = await imu.read_gyroscope()
print(f"Rotation: X={gyro[0]:.2f}°/s Y={gyro[1]:.2f}°/s Z={gyro[2]:.2f}°/s")

# Lecture température (°C)
temp = await imu.read_temperature()
print(f"Température: {temp:.1f}°C")

# Lecture complète
data = await imu.read_all()
print(data)  # {"accelerometer": [...], "gyroscope": [...], "temperature": ...}

# Calibration
await imu.calibrate(samples=100)

# Cleanup
await imu.cleanup()
```

**Caractéristiques:**
- Accéléromètre 3-axis (±2g, ±4g, ±8g, ±16g)
- Gyroscope 3-axis (±250, ±500, ±1000, ±2000 °/s)
- Capteur de température intégré
- Adresse I2C par défaut: 0x68
- Calibration automatique

### 4. PCA9685ServoController (pca9685_servo.py)

**Contrôleur haut niveau pour servomoteurs**

```python
# Via la factory (recommandé)
factory = get_hardware_factory()
servo_controller = await factory.create_servo_controller()

# Contrôle par angle (0-180°)
await servo_controller.set_angle_async(channel=0, angle=90)

# Contrôle multiple
await servo_controller.set_angles_async([
    (0, 90),   # Canal 0 à 90°
    (1, 45),   # Canal 1 à 45°
    (2, 135)   # Canal 2 à 135°
])

# Contrôle PWM direct (avancé)
await servo_controller.set_pwm_async(channel=0, pulse_width=1500)  # 1500µs

# Récupérer l'angle actuel
angle = servo_controller.get_angle(channel=0)

# Reset tous les servos à 90°
await servo_controller.reset_async()

# Cleanup
await servo_controller.cleanup()
```

**Caractéristiques:**
- Contrôle simple par angle (0-180°)
- 16 canaux de servos
- Largeur d'impulsion configurable (défaut 500-2500µs)
- Méthodes async et sync wrapper
- Utilise PCA9685 en interne

## Utilisation avec la Factory (Recommandé)

La **HardwareFactory** gère automatiquement:
- Création de l'interface I2C unique (singleton)
- Initialisation de tous les drivers
- Partage de l'interface I2C entre drivers
- Cleanup ordonné (haut niveau → bas niveau)

### Exemple Complet

```python
import asyncio
from core.hardware.factory import get_hardware_factory
from core.config import get_settings

async def main():
    # 1. Initialiser la factory
    settings = get_settings()
    factory = get_hardware_factory(settings)
    
    try:
        # 2. Créer les composants nécessaires
        servo_controller = await factory.create_servo_controller()
        adc = await factory.get_adc()
        imu = await factory.get_imu()
        
        # 3. Utiliser les composants
        await servo_controller.set_angle_async(0, 90)
        voltage = await adc.read_channel(0)
        accel = await imu.read_accelerometer()
        
        print(f"Servo 0: 90°")
        print(f"Tension canal 0: {voltage:.2f}V")
        print(f"Accélération: {accel}")
        
    finally:
        # 4. Cleanup automatique de tous les composants
        await factory.cleanup_all()

if __name__ == "__main__":
    asyncio.run(main())
```

## Principes de l'Architecture HAL

### 1. Découplage Hardware

Tous les drivers utilisent `I2CInterface` au lieu de dépendances directes:
- ❌ **Avant**: `import smbus` directement dans chaque driver
- ✅ **Maintenant**: Interface `I2CInterface` injectée

### 2. Testabilité

Tous les drivers sont 100% testables sans hardware:
```python
# Dans les tests
mock_i2c = Mock(spec=I2CInterface)
mock_i2c.write_byte_data = AsyncMock()
adc = ADC(i2c=mock_i2c, address=0x48)
```

### 3. Code Async

Toutes les opérations I2C sont asynchrones:
```python
# Bon
await adc.read_channel(0)

# Mauvais (ancien code)
adc.read_channel(0)  # Bloquant!
```

### 4. Gestion d'Erreurs

Tous les drivers implémentent:
- Logging structuré avec structlog
- Gestion d'exceptions propre
- Statuts hardware (READY, ERROR, DISCONNECTED)

### 5. Interface Commune

Tous les drivers implémentent `IHardwareComponent`:
```python
await driver.initialize()  # Initialisation
driver.is_available()      # Vérifier disponibilité
driver.get_status()        # Récupérer statut
await driver.cleanup()     # Nettoyage
```

## Tests

### Tests Unitaires

```bash
# Tests ADC
pytest tests/unit/test_adc.py -v

# Tests IMU
pytest tests/unit/test_imu.py -v
```

### Tests d'Intégration

```bash
# Tests factory complète
pytest tests/integration/test_hardware_factory.py -v
```

## Migration depuis l'Ancien Code

### Avant (Code Legacy)

```python
import smbus

bus = smbus.SMBus(1)
bus.write_byte_data(0x40, 0x00, 0x00)  # Bloquant, pas testable
```

### Après (Architecture HAL)

```python
from core.hardware.factory import get_hardware_factory

factory = get_hardware_factory()
pca9685 = await factory.get_pca9685()  # Async, testable, clean
await pca9685.set_pwm(0, 0, 2048)
```

## Dépendances

- `python-smbus`: Communication I2C bas niveau
- `structlog`: Logging structuré
- `pytest`, `pytest-asyncio`: Tests

Installation:
```bash
pip install python-smbus structlog pytest pytest-asyncio
```

## Troubleshooting

### Erreur I2C

```
OSError: [Errno 121] Remote I/O error
```
➡️ Vérifier connexions I2C et adresses des composants.

### Driver non disponible

```python
if not driver.is_available():
    print("Driver non initialisé!")
    await driver.initialize()
```

### Cleanup non fait

Toujours faire le cleanup:
```python
try:
    await driver.initialize()
    # ... utilisation
finally:
    await driver.cleanup()  # Toujours cleanup!
```

## Contributions

Pour ajouter un nouveau driver:

1. Implémenter `IHardwareComponent`
2. Utiliser `I2CInterface` pour communications
3. Rendre toutes opérations async
4. Ajouter logging avec structlog
5. Créer tests unitaires
6. Ajouter à la factory
7. Documenter ici

## Licence

Voir LICENSE.txt à la racine du projet.
