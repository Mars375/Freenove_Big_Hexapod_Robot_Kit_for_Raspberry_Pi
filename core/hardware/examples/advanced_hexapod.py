#!/usr/bin/env python3
"""
Exemple avancé: Contrôle d'hexapode avec la stack HAL

Cet exemple démontre:
- Gestion multi-servos pour les 6 pattes (18 servos)
- Calibration et positions de sécurité
- Gestion d'erreurs robuste
- Pattern factory pour production
"""

import time
import logging
from typing import List, Tuple
from dataclasses import dataclass
from core.hardware.factory import HardwareFactory
from core.hardware.interfaces.i2c_interface import I2CInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LegServos:
    """Configuration des servos pour une patte"""
    coxa: int  # Servo rotation (base)
    femur: int  # Servo cuisse
    tibia: int  # Servo tibia


class HexapodController:
    """Contrôleur d'hexapode utilisant la stack HAL"""
    
    # Mapping des servos pour les 6 pattes
    LEGS = [
        LegServos(coxa=0, femur=1, tibia=2),    # Patte avant droite
        LegServos(coxa=3, femur=4, tibia=5),    # Patte milieu droite
        LegServos(coxa=6, femur=7, tibia=8),    # Patte arrière droite
        LegServos(coxa=9, femur=10, tibia=11),  # Patte avant gauche
        LegServos(coxa=12, femur=13, tibia=14), # Patte milieu gauche
        LegServos(coxa=15, femur=16, tibia=17), # Patte arrière gauche
    ]
    
    # Positions de sécurité (home position)
    HOME_POSITIONS = {
        'coxa': 90,   # Position neutre
        'femur': 90,  # Cuisse horizontale
        'tibia': 90,  # Tibia à 90°
    }
    
    def __init__(self):
        """Initialise le contrôleur avec la factory HAL"""
        self.factory = HardwareFactory()
        self.servo_controller = self.factory.get_servo_controller()
        self.imu = self.factory.get_imu()
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialise tous les servos à la position de sécurité"""
        logger.info("Initialisation de l'hexapode...")
        
        try:
            # Vérifier la disponibilité du hardware
            if not self._check_hardware():
                return False
            
            # Mettre tous les servos en position home
            self.move_to_home()
            
            # Vérifier l'IMU pour la stabilité
            if self.imu.is_available():
                accel = self.imu.read_accelerometer()
                logger.info(f"IMU calibration: {accel}")
            
            self._initialized = True
            logger.info("✓ Hexapode initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            return False
    
    def _check_hardware(self) -> bool:
        """Vérifie la disponibilité du hardware"""
        # Vérifier la connexion I2C
        i2c = self.factory._i2c_interface
        devices = i2c.scan_bus()
        
        if not devices:
            logger.error("Aucun périphérique I2C détecté!")
            return False
        
        logger.info(f"Périphériques I2C: {[hex(addr) for addr in devices]}")
        return True
    
    def move_to_home(self):
        """Déplace tous les servos à la position home"""
        logger.info("Position HOME pour toutes les pattes...")
        
        for leg_idx, leg in enumerate(self.LEGS):
            logger.info(f"Patte {leg_idx + 1}")
            self.servo_controller.set_angle(leg.coxa, self.HOME_POSITIONS['coxa'])
            self.servo_controller.set_angle(leg.femur, self.HOME_POSITIONS['femur'])
            self.servo_controller.set_angle(leg.tibia, self.HOME_POSITIONS['tibia'])
            time.sleep(0.05)  # Délai pour stabilité
    
    def set_leg_position(self, leg_idx: int, coxa: float, femur: float, tibia: float):
        """Définit la position d'une patte spécifique"""
        if not 0 <= leg_idx < len(self.LEGS):
            raise ValueError(f"Index de patte invalide: {leg_idx}")
        
        leg = self.LEGS[leg_idx]
        
        # Sécurité: limiter les angles
        coxa = max(0, min(180, coxa))
        femur = max(0, min(180, femur))
        tibia = max(0, min(180, tibia))
        
        self.servo_controller.set_angle(leg.coxa, coxa)
        self.servo_controller.set_angle(leg.femur, femur)
        self.servo_controller.set_angle(leg.tibia, tibia)
    
    def wave_gesture(self):
        """Fait un geste de salut avec la patte avant droite"""
        if not self._initialized:
            logger.error("Hexapode non initialisé!")
            return
        
        logger.info("Geste de salut...")
        leg_idx = 0  # Patte avant droite
        
        # Lever la patte
        for angle in range(90, 45, -5):
            self.set_leg_position(leg_idx, 90, angle, 90)
            time.sleep(0.05)
        
        # Mouvement de vague
        for _ in range(3):
            self.set_leg_position(leg_idx, 90, 45, 45)
            time.sleep(0.2)
            self.set_leg_position(leg_idx, 90, 45, 135)
            time.sleep(0.2)
        
        # Reposer la patte
        self.set_leg_position(leg_idx, 90, 90, 90)
    
    def walk_forward(self, steps: int = 3):
        """Marche avant simple (tripod gait)"""
        if not self._initialized:
            logger.error("Hexapode non initialisé!")
            return
        
        logger.info(f"Marche avant ({steps} pas)...")
        
        # Groupes pour tripod gait
        group1 = [0, 2, 4]  # Pattes droites avant/arrière + milieu gauche
        group2 = [1, 3, 5]  # Pattes gauches avant/arrière + milieu droite
        
        for step in range(steps):
            logger.info(f"Pas {step + 1}/{steps}")
            
            # Groupe 1: lever et avancer
            for leg_idx in group1:
                self.set_leg_position(leg_idx, 90, 60, 60)  # Lever
                time.sleep(0.1)
                self.set_leg_position(leg_idx, 120, 60, 60)  # Avancer
                time.sleep(0.1)
                self.set_leg_position(leg_idx, 120, 90, 90)  # Poser
                time.sleep(0.1)
            
            # Groupe 2: lever et avancer
            for leg_idx in group2:
                self.set_leg_position(leg_idx, 90, 60, 60)
                time.sleep(0.1)
                self.set_leg_position(leg_idx, 60, 60, 60)
                time.sleep(0.1)
                self.set_leg_position(leg_idx, 60, 90, 90)
                time.sleep(0.1)
    
    def monitor_stability(self, duration: float = 5.0):
        """Surveille la stabilité avec l'IMU"""
        if not self.imu.is_available():
            logger.warning("IMU non disponible")
            return
        
        logger.info(f"Surveillance stabilité pendant {duration}s...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            accel = self.imu.read_accelerometer()
            gyro = self.imu.read_gyroscope()
            
            # Détecter inclinaison excessive
            if abs(accel[0]) > 15 or abs(accel[1]) > 15:
                logger.warning(f"⚠ Inclinaison détectée! Accél: {accel}")
            
            time.sleep(0.5)
    
    def emergency_stop(self):
        """Arrêt d'urgence: retour position sécurité"""
        logger.warning("🛑 ARRÊT D'URGENCE!")
        self.move_to_home()
    
    def cleanup(self):
        """Nettoyage des ressources"""
        logger.info("Nettoyage des ressources...")
        self.move_to_home()
        self.factory.cleanup()
        self._initialized = False


def main():
    """Exemple d'utilisation du contrôleur d'hexapode"""
    hexapod = HexapodController()
    
    try:
        # Initialisation
        if not hexapod.initialize():
            logger.error("❌ Échec de l'initialisation")
            return
        
        # Attendre stabilisation
        time.sleep(1)
        
        # Séquence de démonstration
        logger.info("=== DÉMARRAGE DÉMONSTRATION ===")
        
        # 1. Geste de salut
        hexapod.wave_gesture()
        time.sleep(1)
        
        # 2. Marche avant
        hexapod.walk_forward(steps=3)
        time.sleep(1)
        
        # 3. Surveillance stabilité
        hexapod.monitor_stability(duration=5)
        
        logger.info("=== DÉMONSTRATION TERMINÉE ===")
        
    except KeyboardInterrupt:
        logger.info("\nInterruption utilisateur")
        hexapod.emergency_stop()
    
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        hexapod.emergency_stop()
    
    finally:
        hexapod.cleanup()


if __name__ == "__main__":
    main()
