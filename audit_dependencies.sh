#!/bin/bash
echo "🔍 AUDIT DÉPENDANCES"
echo "===================="

echo -e "\n📦 Python packages installés:"
pip list | grep -E "(fastapi|uvicorn|picamera|lgpio|gpiozero|adafruit|opencv|structlog)"

echo -e "\n🔌 I2C Devices:"
i2cdetect -y 1

echo -e "\n📸 Caméra:"
vcgencmd get_camera

echo -e "\n🎮 GPIO Groups:"
groups | grep -E "(gpio|i2c|spi)"

echo -e "\n💾 Espace disque:"
df -h | grep -E "(Filesystem|/dev/root)"

echo -e "\n🧠 Mémoire:"
free -h

echo -e "\n🌐 Ports ouverts:"
sudo netstat -tuln | grep -E "(8000|6379)"
