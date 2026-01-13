"""Tests unitaires pour le driver IMU (MPU6050)."""
import pytest
from unittest.mock import Mock, AsyncMock

from core.hardware.drivers.imu import MPU6050
from core.hardware.interfaces.base import HardwareStatus


class TestMPU6050:
    """Suite de tests pour le driver MPU6050 (IMU)."""
    
    @pytest.fixture
    def mock_i2c(self):
        """Crée un mock I2CInterface."""
        mock = Mock()
        mock.write_byte_data = AsyncMock()
        mock.read_byte_data = AsyncMock()
        mock.read_i2c_block_data = AsyncMock()
        return mock
    
    @pytest.fixture
    def mpu6050(self, mock_i2c):
        """Crée une instance MPU6050 avec un mock I2C."""
        return MPU6050(i2c=mock_i2c, address=0x68)
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mpu6050, mock_i2c):
        """Test d'initialisation réussie du MPU6050."""
        # Arrange
        mock_i2c.read_byte_data.return_value = 0x68  # WHO_AM_I
        
        # Act
        result = await mpu6050.initialize()
        
        # Assert
        assert result is True
        assert mpu6050.get_status()["status"] == HardwareStatus.READY.value
        # Vérifier que power management a été configuré
        mock_i2c.write_byte_data.assert_called()
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, mpu6050, mock_i2c):
        """Test d'échec d'initialisation du MPU6050."""
        # Arrange
        mock_i2c.write_byte_data.side_effect = Exception("I2C error")
        
        # Act
        result = await mpu6050.initialize()
        
        # Assert
        assert result is False
        assert mpu6050.get_status()["status"] == HardwareStatus.ERROR.value
    
    @pytest.mark.asyncio
    async def test_read_accelerometer(self, mpu6050, mock_i2c):
        """Test de lecture de l'accéléromètre."""
        # Arrange
        await mpu6050.initialize()
        # Simuler des données accéléromètre (6 bytes)
        mock_i2c.read_i2c_block_data.return_value = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        # Act
        accel = await mpu6050.read_accelerometer()
        
        # Assert
        assert accel is not None
        assert len(accel) == 3  # x, y, z
        assert all(isinstance(v, (int, float)) for v in accel)
    
    @pytest.mark.asyncio
    async def test_read_gyroscope(self, mpu6050, mock_i2c):
        """Test de lecture du gyroscope."""
        # Arrange
        await mpu6050.initialize()
        # Simuler des données gyroscope (6 bytes)
        mock_i2c.read_i2c_block_data.return_value = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        # Act
        gyro = await mpu6050.read_gyroscope()
        
        # Assert
        assert gyro is not None
        assert len(gyro) == 3  # x, y, z
        assert all(isinstance(v, (int, float)) for v in gyro)
    
    @pytest.mark.asyncio
    async def test_read_temperature(self, mpu6050, mock_i2c):
        """Test de lecture de la température."""
        # Arrange
        await mpu6050.initialize()
        # Simuler des données de température (2 bytes)
        # Temp = 25°C environ
        mock_i2c.read_i2c_block_data.return_value = [0x0C, 0x68]  # Valeur brute
        
        # Act
        temp = await mpu6050.read_temperature()
        
        # Assert
        assert temp is not None
        assert isinstance(temp, (int, float))
        # La température devrait être dans une plage raisonnable
        assert -40 <= temp <= 85  # Plage opérationnelle du MPU6050
    
    @pytest.mark.asyncio
    async def test_read_all_data(self, mpu6050, mock_i2c):
        """Test de lecture de toutes les données simultanément."""
        # Arrange
        await mpu6050.initialize()
        # Simuler 14 bytes (accel + temp + gyro)
        mock_i2c.read_i2c_block_data.return_value = [0] * 14
        
        # Act
        data = await mpu6050.read_all()
        
        # Assert
        assert data is not None
        assert "accelerometer" in data
        assert "gyroscope" in data
        assert "temperature" in data
        assert len(data["accelerometer"]) == 3
        assert len(data["gyroscope"]) == 3
        assert isinstance(data["temperature"], (int, float))
    
    @pytest.mark.asyncio
    async def test_calibrate(self, mpu6050, mock_i2c):
        """Test de calibration de l'IMU."""
        # Arrange
        await mpu6050.initialize()
        mock_i2c.read_i2c_block_data.return_value = [0] * 6
        
        # Act
        await mpu6050.calibrate(samples=10)
        
        # Assert
        # Vérifier que plusieurs lectures ont été faites
        assert mock_i2c.read_i2c_block_data.call_count >= 10
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mpu6050):
        """Test du nettoyage du MPU6050."""
        # Arrange
        await mpu6050.initialize()
        
        # Act
        await mpu6050.cleanup()
        
        # Assert
        status = mpu6050.get_status()
        assert status["status"] == HardwareStatus.DISCONNECTED.value
    
    def test_is_available_before_init(self, mpu6050):
        """Test de disponibilité avant initialisation."""
        assert mpu6050.is_available() is False
    
    @pytest.mark.asyncio
    async def test_is_available_after_init(self, mpu6050):
        """Test de disponibilité après initialisation."""
        await mpu6050.initialize()
        assert mpu6050.is_available() is True
    
    def test_get_status(self, mpu6050):
        """Test de récupération du statut."""
        status = mpu6050.get_status()
        
        assert "type" in status
        assert status["type"] == "mpu6050"
        assert "address" in status
        assert "status" in status
        assert "available" in status
    
    @pytest.mark.asyncio
    async def test_data_conversion_accelerometer(self, mpu6050, mock_i2c):
        """Test de conversion des données brutes de l'accéléromètre."""
        # Arrange
        await mpu6050.initialize()
        # Valeur max positive 16-bit signé = 32767
        mock_i2c.read_i2c_block_data.return_value = [0x7F, 0xFF, 0x00, 0x00, 0x00, 0x00]
        
        # Act
        accel = await mpu6050.read_accelerometer()
        
        # Assert
        # Les valeurs devraient être converties en g (gravité)
        assert accel[0] > 0  # X devrait être positif
        # Plage typique: ±2g, ±4g, ±8g, ou ±16g selon config
        assert abs(accel[0]) <= 16  # Maximum possible
    
    @pytest.mark.asyncio
    async def test_data_conversion_gyroscope(self, mpu6050, mock_i2c):
        """Test de conversion des données brutes du gyroscope."""
        # Arrange
        await mpu6050.initialize()
        # Valeur max positive
        mock_i2c.read_i2c_block_data.return_value = [0x7F, 0xFF, 0x00, 0x00, 0x00, 0x00]
        
        # Act
        gyro = await mpu6050.read_gyroscope()
        
        # Assert
        # Les valeurs devraient être converties en deg/s
        assert gyro[0] > 0
        # Plage typique: ±250, ±500, ±1000, ou ±2000 deg/s
        assert abs(gyro[0]) <= 2000
    
    @pytest.mark.asyncio
    async def test_read_without_initialization(self, mpu6050):
        """Test de lecture sans initialisation préalable."""
        # Act & Assert
        with pytest.raises(RuntimeError):
            await mpu6050.read_accelerometer()
    
    @pytest.mark.asyncio
    async def test_multiple_reads_stability(self, mpu6050, mock_i2c):
        """Test de stabilité sur plusieurs lectures."""
        # Arrange
        await mpu6050.initialize()
        mock_i2c.read_i2c_block_data.return_value = [0x00, 0x10] * 3
        
        # Act
        accel1 = await mpu6050.read_accelerometer()
        accel2 = await mpu6050.read_accelerometer()
        
        # Assert
        # Avec les mêmes données mock, les résultats doivent être identiques
        assert accel1 == accel2
