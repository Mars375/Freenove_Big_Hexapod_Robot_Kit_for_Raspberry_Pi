"""Tests unitaires pour le driver ADC."""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from core.hardware.drivers.adc import ADC
from core.hardware.interfaces.base import HardwareStatus


class TestADC:
    """Suite de tests pour le driver ADC."""
    
    @pytest.fixture
    def mock_i2c(self):
        """Crée un mock I2CInterface."""
        mock = Mock()
        mock.write_byte_data = AsyncMock()
        mock.read_byte_data = AsyncMock()
        mock.write_i2c_block_data = AsyncMock()
        mock.read_i2c_block_data = AsyncMock(return_value=[0x00, 0x00])
        return mock
    
    @pytest.fixture
    def adc(self, mock_i2c):
        """Crée une instance ADC avec un mock I2C."""
        return ADC(i2c=mock_i2c, address=0x48)
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, adc, mock_i2c):
        """Test d'initialisation réussie de l'ADC."""
        # Arrange
        mock_i2c.read_byte_data.return_value = 0x00
        
        # Act
        result = await adc.initialize()
        
        # Assert
        assert result is True
        assert adc.get_status()["status"] == HardwareStatus.READY.value
        mock_i2c.write_byte_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, adc, mock_i2c):
        """Test d'échec d'initialisation de l'ADC."""
        # Arrange
        mock_i2c.write_byte_data.side_effect = Exception("I2C error")
        
        # Act
        result = await adc.initialize()
        
        # Assert
        assert result is False
        assert adc.get_status()["status"] == HardwareStatus.ERROR.value
    
    @pytest.mark.asyncio
    async def test_read_channel_valid(self, adc, mock_i2c):
        """Test de lecture d'un canal valide."""
        # Arrange
        await adc.initialize()
        # Simuler une lecture de valeur 2.5V (2048 en 12-bit pour 3.3V ref)
        mock_i2c.read_i2c_block_data.return_value = [0x08, 0x00]  # 0x0800 = 2048
        
        # Act
        value = await adc.read_channel(0)
        
        # Assert
        assert value is not None
        assert 0 <= value <= 3.3  # Tension de référence
        mock_i2c.write_i2c_block_data.assert_called()
        mock_i2c.read_i2c_block_data.assert_called()
    
    @pytest.mark.asyncio
    async def test_read_channel_invalid(self, adc):
        """Test de lecture d'un canal invalide."""
        # Arrange
        await adc.initialize()
        
        # Act & Assert
        with pytest.raises(ValueError):
            await adc.read_channel(4)  # ADC n'a que 4 canaux (0-3)
    
    @pytest.mark.asyncio
    async def test_read_all_channels(self, adc, mock_i2c):
        """Test de lecture de tous les canaux."""
        # Arrange
        await adc.initialize()
        mock_i2c.read_i2c_block_data.return_value = [0x08, 0x00]
        
        # Act
        values = await adc.read_all_channels()
        
        # Assert
        assert len(values) == 4
        assert all(0 <= v <= 3.3 for v in values)
    
    @pytest.mark.asyncio
    async def test_read_voltage(self, adc, mock_i2c):
        """Test de conversion de valeur brute en tension."""
        # Arrange
        await adc.initialize()
        # Valeur max 12-bit = 4095 devrait donner 3.3V
        mock_i2c.read_i2c_block_data.return_value = [0x0F, 0xFF]  # 0x0FFF = 4095
        
        # Act
        voltage = await adc.read_channel(0)
        
        # Assert
        assert voltage is not None
        assert abs(voltage - 3.3) < 0.1  # Tolérance de 0.1V
    
    @pytest.mark.asyncio
    async def test_cleanup(self, adc):
        """Test du nettoyage de l'ADC."""
        # Arrange
        await adc.initialize()
        
        # Act
        await adc.cleanup()
        
        # Assert
        status = adc.get_status()
        assert status["status"] == HardwareStatus.DISCONNECTED.value
    
    def test_is_available_before_init(self, adc):
        """Test de disponibilité avant initialisation."""
        assert adc.is_available() is False
    
    @pytest.mark.asyncio
    async def test_is_available_after_init(self, adc):
        """Test de disponibilité après initialisation."""
        await adc.initialize()
        assert adc.is_available() is True
    
    def test_get_status(self, adc):
        """Test de récupération du statut."""
        status = adc.get_status()
        
        assert "type" in status
        assert status["type"] == "adc"
        assert "address" in status
        assert "status" in status
        assert "available" in status
    
    @pytest.mark.asyncio
    async def test_multiple_reads_consistency(self, adc, mock_i2c):
        """Test de cohérence sur plusieurs lectures."""
        # Arrange
        await adc.initialize()
        mock_i2c.read_i2c_block_data.return_value = [0x08, 0x00]
        
        # Act
        value1 = await adc.read_channel(0)
        value2 = await adc.read_channel(0)
        
        # Assert
        assert value1 == value2  # Même valeur mock, doit être identique
    
    @pytest.mark.asyncio
    async def test_read_without_initialization(self, adc):
        """Test de lecture sans initialisation préalable."""
        # Act & Assert
        # Devrait échouer ou retourner None car non initialisé
        with pytest.raises(RuntimeError):
            await adc.read_channel(0)
