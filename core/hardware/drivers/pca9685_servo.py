"""Contrôleur de servos PCA9685 utilisant le HAL."""
import logging
from typing import Optional, List, Tuple, Dict, Any

from core.hardware.interfaces.servo_controller import IServoController
from core.hardware.drivers.pca9685 import PCA9685


class PCA9685ServoController(IServoController):
    """Contrôleur de servos utilisant le driver PCA9685 avec HAL.
    
    Gère jusqu'à 16 servos par chip PCA9685 via notre architecture HAL.
    Permet un contrôle par angle (0-180°) ou par largeur d'impulsion (µs).
    
    Architecture:
        - Utilise le driver PCA9685 qui communique via I2CInterface HAL
        - Pas de dépendance directe à smbus ou adafruit
        - Compatible avec l'architecture de découplage hardware
    
    Configuration matérielle:
        - PCA9685 connecté via I2C (adresse par défaut 0x40)
        - Servos connectés aux canaux 0-15
        - Alimentation 5-6V pour servos (séparée du Pi)
        - Masse commune entre Pi et alimentation servos
    """
    
    def __init__(
        self,
        pca_low: PCA9685,
        pca_high: PCA9685,
        min_pulse: int = 500,
        max_pulse: int = 2500
    ):
        """Initialise le contrôleur de servos.
        
        Args:
            pca_low: Driver PCA9685 pour canaux 0-15 (Address 0x41)
            pca_high: Driver PCA9685 pour canaux 16-31 (Address 0x40)
            min_pulse: Largeur d'impulsion minimale en µs (défaut 500)
            max_pulse: Largeur d'impulsion maximale en µs (défaut 2500)
        """
        self._pca_low = pca_low
        self._pca_high = pca_high
        self._min_pulse = min_pulse
        self._max_pulse = max_pulse
        self._current_angles: Dict[int, int] = {}
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(
            f"PCA9685ServoController créé avec pulse range {min_pulse}-{max_pulse}µs"
        )
    
    async def initialize(self) -> None:
        """Initialise le contrôleur (les PCA9685 doivent déjà être initialisés)."""
        if not self._pca_low.is_available() or not self._pca_high.is_available():
            self.logger.warning("Un ou plusieurs PCA9685 non disponibles")
        else:
            self.logger.info("PCA9685ServoController (Dual Board) prêt")
    
    def is_available(self) -> bool:
        """Vérifie si le contrôleur est disponible."""
        return self._pca_low.is_available() and self._pca_high.is_available()
    
    def _angle_to_pulse(self, angle: int) -> int:
        """Convertit un angle (0-180°) en largeur d'impulsion (µs).
        
        Args:
            angle: Angle en degrés (0-180)
            
        Returns:
            Largeur d'impulsion en microsecondes
        """
        if not 0 <= angle <= 180:
            raise ValueError(f"Angle {angle} hors limites (0-180)")
        
        # Interpolation linéaire: angle 0° = min_pulse, 180° = max_pulse
        pulse = self._min_pulse + (angle / 180.0) * (self._max_pulse - self._min_pulse)
        return int(pulse)
    
    def _pulse_to_angle(self, pulse: int) -> int:
        """Convertit une largeur d'impulsion (µs) en angle (0-180°).
        
        Args:
            pulse: Largeur d'impulsion en microsecondes
            
        Returns:
            Angle en degrés
        """
        angle = (pulse - self._min_pulse) / (self._max_pulse - self._min_pulse) * 180
        return int(max(0, min(180, angle)))
    
    def set_angle(self, channel: int, angle: int) -> None:
        """Définit l'angle d'un servo (méthode synchrone wrapper).
        
        Args:
            channel: Numéro du canal (0-31)
            angle: Angle cible en degrés (0-180)
            
        Raises:
            ValueError: Si channel ou angle hors limites
            RuntimeError: Si PCA9685 non disponible
        """
        import asyncio
        
        try:
            # Utiliser asyncio.run uniquement si pas dans une boucle existante
            try:
                loop = asyncio.get_running_loop()
                # Si on est déjà dans une loop, créer une tâche
                self.logger.warning(
                    "set_angle appelé depuis code async, utiliser set_angle_async à la place"
                )
                asyncio.create_task(self.set_angle_async(channel, angle))
            except RuntimeError:
                # Pas de loop en cours, on peut utiliser asyncio.run
                asyncio.run(self.set_angle_async(channel, angle))
        except Exception as e:
            self.logger.error(f"Erreur set_angle channel {channel}: {e}")
            raise
    
    async def set_angle_async(self, channel: int, angle: int) -> None:
        """Définit l'angle d'un servo (version async).
        
        Routes channels 0-15 to pca_low and 16-31 to pca_high.
        
        Args:
            channel: Numéro du canal (0-31)
            angle: Angle cible en degrés (0-180)
            
        Raises:
            ValueError: Si channel ou angle hors limites
            RuntimeError: Si PCA9685 non disponible
        """
        if not self.is_available():
            raise RuntimeError("PCA9685 non disponible")
        
        if not 0 <= channel < 32:
            raise ValueError(f"Canal {channel} hors limites (0-31)")
        
        if not 0 <= angle <= 180:
            raise ValueError(f"Angle {angle} hors limites (0-180)")
        
        try:
            pulse = self._angle_to_pulse(angle)
            
            # Routing logic
            if channel < 16:
                await self._pca_low.set_servo_pulse(channel, pulse)
            else:
                await self._pca_high.set_servo_pulse(channel - 16, pulse)
                
            self._current_angles[channel] = angle
            
            self.logger.debug(
                f"Servo {channel}: angle={angle}° (pulse={pulse}µs)"
            )
            
        except Exception as e:
            self.logger.error(
                f"Échec set_angle_async channel {channel}, angle {angle}: {e}"
            )
            raise
    
    def set_angles(self, angles: List[Tuple[int, int]]) -> None:
        """Définit plusieurs angles de servos (méthode synchrone wrapper).
        
        Args:
            angles: Liste de tuples (channel, angle)
        """
        import asyncio
        
        try:
            try:
                loop = asyncio.get_running_loop()
                self.logger.warning(
                    "set_angles appelé depuis code async, utiliser set_angles_async"
                )
                asyncio.create_task(self.set_angles_async(angles))
            except RuntimeError:
                asyncio.run(self.set_angles_async(angles))
        except Exception as e:
            self.logger.error(f"Erreur set_angles: {e}")
            raise
    
    async def set_angles_async(self, angles: List[Tuple[int, int]]) -> None:
        """Définit plusieurs angles de servos (version async).
        
        Args:
            angles: Liste de tuples (channel, angle)
        """
        for channel, angle in angles:
            await self.set_angle_async(channel, angle)
        
        self.logger.debug(f"Configuré {len(angles)} servos")
    
    def get_angle(self, channel: int) -> Optional[int]:
        """Récupère le dernier angle défini pour un servo.
        
        Note: Retourne l'angle commandé, pas la position réelle.
        Le PCA9685 n'a pas de retour de position.
        
        Args:
            channel: Numéro du canal
            
        Returns:
            Dernier angle commandé ou None si jamais défini
        """
        return self._current_angles.get(channel)
    
    def set_pwm(self, channel: int, pulse_width: int) -> None:
        """Définit la largeur d'impulsion PWM brute (méthode synchrone wrapper).
        
        Args:
            channel: Numéro du canal
            pulse_width: Largeur d'impulsion en µs
        """
        import asyncio
        
        try:
            try:
                loop = asyncio.get_running_loop()
                self.logger.warning(
                    "set_pwm appelé depuis code async, utiliser set_pwm_async"
                )
                asyncio.create_task(self.set_pwm_async(channel, pulse_width))
            except RuntimeError:
                asyncio.run(self.set_pwm_async(channel, pulse_width))
        except Exception as e:
            self.logger.error(f"Erreur set_pwm: {e}")
            raise
    
    async def set_pwm_async(self, channel: int, pulse_width: int) -> None:
        """Définit la largeur d'impulsion PWM brute (version async).
        
        Méthode avancée pour un contrôle fin.
        
        Args:
            channel: Numéro du canal (0-31)
            pulse_width: Largeur d'impulsion en µs
            
        Raises:
            ValueError: Si valeurs hors limites
            RuntimeError: Si PCA9685 non disponible
        """
        if not self.is_available():
            raise RuntimeError("PCA9685 non disponible")
        
        if not 0 <= channel < 32:
            raise ValueError(f"Canal {channel} hors limites (0-31)")
        
        if not self._min_pulse <= pulse_width <= self._max_pulse:
            raise ValueError(
                f"Pulse width {pulse_width} hors limites "
                f"({self._min_pulse}-{self._max_pulse})"
            )
        
        try:
            if channel < 16:
                await self._pca_low.set_servo_pulse(channel, pulse_width)
            else:
                await self._pca_high.set_servo_pulse(channel - 16, pulse_width)
            
            # Estimer l'angle pour le tracking
            angle = self._pulse_to_angle(pulse_width)
            self._current_angles[channel] = angle
            
            self.logger.debug(
                f"Servo {channel}: PWM={pulse_width}µs (angle≈{angle}°)"
            )
            
        except Exception as e:
            self.logger.error(
                f"Échec set_pwm_async channel {channel}, pulse {pulse_width}: {e}"
            )
            raise
    
    async def cleanup(self) -> None:
        """Nettoyage du contrôleur (désactive les sorties)."""
        self.logger.info("Nettoyage PCA9685ServoController")
        
        try:
            await self.relax()
            self._current_angles.clear()
            self.logger.info("PCA9685ServoController nettoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du cleanup: {e}")
    
    async def relax(self) -> None:
        """Désactive tous les servos (Full OFF)."""
        self.logger.info("Relaxing all servos (Full OFF)")
        # PCA9685 Full OFF bit is bit 4 of LEDn_OFF_H (value 4096 / 0x1000)
        # Our set_all_pwm handles the register writing.
        await self._pca_low.set_all_pwm(0, 4096)
        await self._pca_high.set_all_pwm(0, 4096)
        self._current_angles.clear()
    
    def reset(self) -> None:
        """Remet tous les servos en position neutre (90°)."""
        import asyncio
        
        try:
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self.reset_async())
            except RuntimeError:
                asyncio.run(self.reset_async())
        except Exception as e:
            self.logger.error(f"Erreur reset: {e}")
            raise
    
    async def reset_async(self) -> None:
        """Remet tous les servos en position neutre (90°) - version async."""
        self.logger.info("Reset de tous les servos à 90°")
        
        for channel in range(32):
            try:
                await self.set_angle_async(channel, 90)
            except Exception as e:
                self.logger.warning(
                    f"Échec reset servo {channel}: {e}"
                )
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du contrôleur."""
        return {
            "type": "pca9685_servo_controller_dual",
            "available": self.is_available(),
            "min_pulse": self._min_pulse,
            "max_pulse": self._max_pulse,
            "current_angles": dict(self._current_angles),
            "pca_low_status": self._pca_low.get_status(),
            "pca_high_status": self._pca_high.get_status()
        }
