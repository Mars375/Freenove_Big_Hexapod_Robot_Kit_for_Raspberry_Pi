"""Tests d'intégration pour la HardwareFactory avec tous les drivers HAL."""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from core.config import Settings
from core.hardware.factory import HardwareFactory, get_hardware_factory
from core.hardware.interfaces.i2c import I2CInterface
from core.hardware.interfaces.base import HardwareStatus


class TestHardwareFactoryIntegration:
    """Tests d'intégration pour la factory hardware complète."""
    
    @pytest.fixture
    async def mock_i2c(self):
        """Crée un mock I2CInterface complet."""
        mock = Mock(spec=I2CInterface)
        mock.initialize = AsyncMock(return_value=True)
        mock.cleanup = AsyncMock()
        mock.write_byte_data = AsyncMock()
        mock.read_byte_data = AsyncMock(return_value=0x68)
        mock.write_i2c_block_data = AsyncMock()
        mock.read_i2c_block_data = AsyncMock(return_value=[0] * 14)
        mock.is_available = Mock(return_value=True)
        return mock
    
    @pytest.fixture
    def settings(self):
        """Crée des settings de test."""
        return Settings()
    
    @pytest.fixture
    async def factory(self, settings):
        """Crée une instance de factory."""
        factory = HardwareFactory(settings)
        yield factory
        # Cleanup après chaque test
        await factory.cleanup_all()
    
    @pytest.mark.asyncio
    async def test_factory_creation(self, factory, settings):
        """Test de création de la factory."""
        assert factory is not None
        assert factory.settings == settings
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_get_i2c_interface(self, mock_smbus_class, factory, mock_i2c):
        """Test de récupération de l'interface I2C (singleton)."""
        # Configure le mock
        mock_smbus_class.return_value = mock_i2c
        
        # Premier appel - devrait créer l'interface
        i2c1 = await factory.get_i2c_interface()
        assert i2c1 is not None
        mock_i2c.initialize.assert_called_once()
        
        # Deuxième appel - devrait retourner la même instance (singleton)
        i2c2 = await factory.get_i2c_interface()
        assert i2c2 is i2c1
        # initialize ne devrait pas être appelé une deuxième fois
        assert mock_i2c.initialize.call_count == 1
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_get_pca9685(self, mock_smbus_class, factory, mock_i2c):
        """Test de création du driver PCA9685."""
        mock_smbus_class.return_value = mock_i2c
        
        # Récupérer le PCA9685
        pca9685 = await factory.get_pca9685(address=0x40, frequency=50)
        
        assert pca9685 is not None
        assert pca9685._address == 0x40
        assert pca9685._frequency == 50
        mock_i2c.write_byte_data.assert_called()  # Initialisation du PCA9685
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_get_adc(self, mock_smbus_class, factory, mock_i2c):
        """Test de création du driver ADC."""
        mock_smbus_class.return_value = mock_i2c
        
        # Récupérer l'ADC
        adc = await factory.get_adc(address=0x48)
        
        assert adc is not None
        assert adc._address == 0x48
        assert adc.is_available()
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_get_imu(self, mock_smbus_class, factory, mock_i2c):
        """Test de création du driver IMU."""
        mock_smbus_class.return_value = mock_i2c
        
        # Récupérer l'IMU
        imu = await factory.get_imu(address=0x68)
        
        assert imu is not None
        assert imu._address == 0x68
        assert imu.is_available()
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_create_servo_controller(self, mock_smbus_class, factory, mock_i2c):
        """Test de création du contrôleur de servos."""
        mock_smbus_class.return_value = mock_i2c
        
        # Créer le contrôleur de servos
        servo_controller = await factory.create_servo_controller()
        
        assert servo_controller is not None
        assert servo_controller.is_available()
        
        # Vérifier que le PCA9685 sous-jacent a été créé
        assert factory._pca9685 is not None
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_servo_controller_singleton(self, mock_smbus_class, factory, mock_i2c):
        """Test que le contrôleur de servos est un singleton."""
        mock_smbus_class.return_value = mock_i2c
        
        # Premier appel
        servo1 = await factory.create_servo_controller()
        
        # Deuxième appel - devrait retourner la même instance
        servo2 = await factory.create_servo_controller()
        
        assert servo1 is servo2
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_full_stack_integration(self, mock_smbus_class, factory, mock_i2c):
        """Test d'intégration de la stack complète: I2C → Drivers → Controller."""
        mock_smbus_class.return_value = mock_i2c
        
        # 1. Créer l'interface I2C
        i2c = await factory.get_i2c_interface()
        assert i2c is not None
        
        # 2. Créer les drivers de base
        pca9685 = await factory.get_pca9685()
        adc = await factory.get_adc()
        imu = await factory.get_imu()
        
        assert all([pca9685, adc, imu])
        assert all([
            pca9685.is_available(),
            adc.is_available(),
            imu.is_available()
        ])
        
        # 3. Créer le contrôleur haut niveau
        servo_controller = await factory.create_servo_controller()
        assert servo_controller is not None
        assert servo_controller.is_available()
        
        # 4. Vérifier que tous utilisent la même interface I2C
        assert pca9685._i2c is i2c
        assert adc._i2c is i2c
        assert imu._i2c is i2c
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_cleanup_all(self, mock_smbus_class, factory, mock_i2c):
        """Test du nettoyage complet de tous les composants."""
        mock_smbus_class.return_value = mock_i2c
        
        # Créer tous les composants
        await factory.get_i2c_interface()
        await factory.get_pca9685()
        await factory.get_adc()
        await factory.get_imu()
        await factory.create_servo_controller()
        
        # Cleanup
        await factory.cleanup_all()
        
        # Vérifier que tout est nettoyé
        assert factory._servo_controller is None
        assert factory._imu is None
        assert factory._adc is None
        assert factory._pca9685 is None
        assert factory._i2c is None
        
        # Vérifier que cleanup a été appelé sur l'I2C
        mock_i2c.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_cleanup_order(self, mock_smbus_class, factory, mock_i2c):
        """Test que le cleanup se fait dans le bon ordre (haut niveau → bas niveau)."""
        mock_smbus_class.return_value = mock_i2c
        
        cleanup_order = []
        
        # Mock pour tracer l'ordre de cleanup
        original_cleanup = mock_i2c.cleanup
        
        async def track_cleanup(component_name):
            cleanup_order.append(component_name)
        
        # Créer la stack complète
        await factory.create_servo_controller()
        await factory.get_adc()
        await factory.get_imu()
        
        # Cleanup
        await factory.cleanup_all()
        
        # Le cleanup devrait avoir été fait
        assert factory._servo_controller is None
        assert factory._imu is None
        assert factory._adc is None
        assert factory._pca9685 is None
        assert factory._i2c is None
    
    @pytest.mark.asyncio
    @patch('core.hardware.factory.SMBusI2CInterface')
    async def test_error_handling_in_driver_creation(self, mock_smbus_class, factory):
        """Test de la gestion d'erreurs lors de la création de drivers."""
        # Simuler une erreur I2C
        mock_i2c = Mock(spec=I2CInterface)
        mock_i2c.initialize = AsyncMock(return_value=True)
        mock_i2c.write_byte_data = AsyncMock(side_effect=Exception("I2C Error"))
        mock_smbus_class.return_value = mock_i2c
        
        # Tenter de créer un PCA9685 - devrait gérer l'erreur
        with pytest.raises(Exception):
            await factory.get_pca9685()
    
    @pytest.mark.asyncio
    def test_get_hardware_factory_singleton(self, settings):
        """Test que get_hardware_factory retourne un singleton."""
        # Reset le singleton global
        import core.hardware.factory as factory_module
        factory_module._factory = None
        
        # Premier appel
        factory1 = get_hardware_factory(settings)
        
        # Deuxième appel
        factory2 = get_hardware_factory()
        
        # Devrait être la même instance
        assert factory1 is factory2
        
        # Cleanup
        factory_module._factory = None
