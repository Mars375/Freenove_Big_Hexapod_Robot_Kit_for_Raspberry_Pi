"""Test servo orientation - pour voir quel côté est inversé"""
import asyncio
from core.hardware.movement import MovementController

async def test():
    controller = MovementController()
    await controller.initialize()
    
    print("\n=== Test orientation servos ===")
    print("Le robot devrait se tenir debout normalement")
    input("Appuie sur Enter pour continuer...")
    
    # Test: pencher à droite (roll positif)
    print("\n1. Pencher à DROITE (roll=+10)")
    await controller.set_attitude(roll=10, pitch=0, yaw=0)
    await asyncio.sleep(2)
    
    # Retour neutre
    print("   Retour neutre")
    await controller.set_attitude(roll=0, pitch=0, yaw=0)
    await asyncio.sleep(1)
    
    # Test: pencher en avant (pitch positif)
    print("\n2. Pencher en AVANT (pitch=+10)")
    await controller.set_attitude(roll=0, pitch=10, yaw=0)
    await asyncio.sleep(2)
    
    # Retour neutre
    print("   Retour neutre")
    await controller.set_attitude(roll=0, pitch=0, yaw=0)
    await asyncio.sleep(1)
    
    print("\n=== Test terminé ===")
    print("Dis-moi ce que tu as observé:")
    print("- Le robot penche-t-il du bon côté ?")
    print("- Les pattes avant/arrière sont-elles correctes ?")

asyncio.run(test())
