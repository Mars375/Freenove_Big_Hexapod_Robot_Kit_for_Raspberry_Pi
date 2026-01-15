#!/usr/bin/env python3
"""
🤖 Tachikoma Terminal Client - VERSION FINALE CORRIGÉE
Compatible avec l'API réelle de Tachikoma
"""
import asyncio
import aiohttp
import sys
import termios
import tty
from typing import Optional

class TachikomaClient:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = True
    
    async def connect(self):
        """Connexion à l'API"""
        timeout = aiohttp.ClientTimeout(total=5)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        try:
            async with self.session.get(f"{self.api_url}/health") as resp:
                if resp.status == 200:
                    print(f"✅ Connecté à {self.api_url}")
                    return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def move(self, mode: str, x: int = 0, y: int = 0, speed: int = 5, angle: int = 0):
        """
        Envoie une commande de mouvement
        mode: "motion", "forward", "backward", etc.
        x: -35 à 35
        y: -35 à 35
        speed: 2 à 10
        angle: -10 à 10
        """
        try:
            payload = {
                "mode": mode,
                "x": x,
                "y": y,
                "speed": speed,
                "angle": angle
            }
            
            async with self.session.post(
                f"{self.api_url}/api/movement/move",
                json=payload
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    action = f"X:{x} Y:{y}" if x or y else f"A:{angle}" if angle else mode
                    print(f"➡️  {action:15s} (speed={speed})", end='\r')
                    return True
                else:
                    text = await resp.text()
                    print(f"❌ Erreur {resp.status}: {text[:200]}")
                    return False
        except Exception as e:
            print(f"❌ Erreur move: {e}")
            return False
    
    async def stop(self):
        """Arrête le robot"""
        try:
            async with self.session.post(f"{self.api_url}/api/movement/stop") as resp:
                if resp.status == 200:
                    print("🛑 STOP            ", end='\r')
                    return True
        except Exception as e:
            print(f"❌ Erreur stop: {e}")
            return False
    
    async def test_walk(self, speed: int = 5, duration: float = 5.0):
        """Test de marche"""
        try:
            async with self.session.post(
                f"{self.api_url}/api/movement/test_walk",
                params={"speed": speed, "duration": duration}
            ) as resp:
                if resp.status == 200:
                    print(f"🚶 Test de marche: speed={speed}, durée={duration}s")
                    return True
        except Exception as e:
            print(f"❌ Erreur test: {e}")
            return False
    
    async def set_led(self, r: int, g: int, b: int):
        """Change la couleur des LEDs"""
        try:
            async with self.session.post(
                f"{self.api_url}/api/leds/color",
                json={"r": r, "g": g, "b": b}
            ) as resp:
                if resp.status == 200:
                    print(f"💡 LED: RGB({r}, {g}, {b})")
                    return True
        except Exception as e:
            print(f"❌ LED error: {e}")
            return False
    
    async def rainbow(self):
        """Mode arc-en-ciel"""
        try:
            async with self.session.post(f"{self.api_url}/api/leds/rainbow") as resp:
                if resp.status == 200:
                    print("🌈 Mode Rainbow activé")
                    return True
        except:
            return False
    
    async def get_sensors(self):
        """Affiche les capteurs"""
        try:
            async with self.session.get(f"{self.api_url}/api/sensors/all") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("\n" + "="*60)
                    battery = data.get('battery', {})
                    print(f"🔋 Batterie: {battery.get('voltage', 0):.2f}V")
                    
                    imu = data.get('imu', {})
                    print(f"📐 IMU: Pitch:{imu.get('pitch', 0):.1f}° Roll:{imu.get('roll', 0):.1f}° Yaw:{imu.get('yaw', 0):.1f}°")
                    
                    ultrasonic = data.get('ultrasonic', {})
                    print(f"📏 Distance: {ultrasonic.get('distance', 0):.1f}cm")
                    print("="*60)
                    return True
        except Exception as e:
            print(f"❌ Erreur capteurs: {e}")
            return False
    
    async def close(self):
        """Ferme la connexion"""
        if self.session:
            await self.session.close()
    
    def print_help(self):
        """Affiche l'aide"""
        print("\n" + "="*60)
        print("🤖 TACHIKOMA - CONTROLES")
        print("="*60)
        print("  W        : Avancer (Y+25)")
        print("  S        : Reculer (Y-25)")
        print("  A        : Gauche (X-25)")
        print("  D        : Droite (X+25)")
        print("  Q        : Rotation gauche (angle -8)")
        print("  E        : Rotation droite (angle +8)")
        print("  SPACE    : Stop")
        print("  T        : Test de marche (5s)")
        print("  I        : Info capteurs")
        print("  1-8      : Couleurs LED (Rouge, Vert, Bleu, Jaune, ...)")
        print("  9        : Arc-en-ciel")
        print("  +/-      : Vitesse ±1 (limites: 2-10)")
        print("  ESC      : Quitter")
        print("  H        : Aide")
        print("="*60)
        print("  Limites API:")
        print("    X/Y: -35 à +35 | Speed: 2 à 10 | Angle: -10 à +10")
        print("="*60)
    
    async def run(self):
        """Boucle principale"""
        if not await self.connect():
            return
        
        self.print_help()
        
        speed = 5  # Vitesse par défaut (2-10)
        
        # Configure le terminal en mode raw
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            print(f"\n🎮 Prêt ! Vitesse: {speed}/10 (H pour aide)\n")
            
            while self.running:
                # Lecture non-bloquante
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    
                    # Mouvements
                    if key.lower() == 'w':
                        await self.move("motion", x=0, y=25, speed=speed)
                    elif key.lower() == 's':
                        await self.move("motion", x=0, y=-25, speed=speed)
                    elif key.lower() == 'a':
                        await self.move("motion", x=-25, y=0, speed=speed)
                    elif key.lower() == 'd':
                        await self.move("motion", x=25, y=0, speed=speed)
                    elif key.lower() == 'q':
                        await self.move("motion", x=0, y=0, speed=speed, angle=-8)
                    elif key.lower() == 'e':
                        await self.move("motion", x=0, y=0, speed=speed, angle=8)
                    elif key == ' ':
                        await self.stop()
                    
                    # Vitesse (2-10)
                    elif key == '+' or key == '=':
                        speed = min(10, speed + 1)
                        print(f"⚡ Vitesse: {speed}/10    ")
                    elif key == '-' or key == '_':
                        speed = max(2, speed - 1)
                        print(f"🐌 Vitesse: {speed}/10    ")
                    
                    # Test
                    elif key.lower() == 't':
                        await self.test_walk(speed=speed, duration=5.0)
                    
                    # LEDs
                    elif key == '1':
                        await self.set_led(255, 0, 0)      # Rouge
                    elif key == '2':
                        await self.set_led(0, 255, 0)      # Vert
                    elif key == '3':
                        await self.set_led(0, 0, 255)      # Bleu
                    elif key == '4':
                        await self.set_led(255, 255, 0)    # Jaune
                    elif key == '5':
                        await self.set_led(255, 0, 255)    # Magenta
                    elif key == '6':
                        await self.set_led(0, 255, 255)    # Cyan
                    elif key == '7':
                        await self.set_led(255, 255, 255)  # Blanc
                    elif key == '8':
                        await self.set_led(0, 0, 0)        # Éteint
                    elif key == '9':
                        await self.rainbow()
                    
                    # Info
                    elif key.lower() == 'i':
                        await self.get_sensors()
                    elif key.lower() == 'h':
                        self.print_help()
                        print(f"Vitesse actuelle: {speed}/10")
                    elif ord(key) == 27:  # ESC
                        print("\n\n👋 Au revoir !")
                        self.running = False
                
                await asyncio.sleep(0.05)
        
        finally:
            # Restaure le terminal
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            await self.stop()
            await self.close()


async def main():
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = input("IP de Tachikoma (Enter = 192.168.1.160): ").strip()
        if not ip:
            ip = "192.168.1.160"
    
    api_url = f"http://{ip}:8000"
    
    client = TachikomaClient(api_url)
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt !")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
