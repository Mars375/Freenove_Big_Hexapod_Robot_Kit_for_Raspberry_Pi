"""Test direction de marche"""
import asyncio
from core.hardware.movement import MovementController

async def test():
    controller = MovementController()
    await controller.initialize()
    
    print("\n=== Test Direction ===")
    print("Position de référence: Raspberry Pi (corps) à l'ARRIÈRE, caméra à l'AVANT")
    input("Mets le robot orienté comme ça, puis Enter...")
    
    print("\n1. Commande FORWARD (devrait avancer vers la caméra)")
    await controller.move("forward", 0, 0, 3, 0)
    await asyncio.sleep(3)
    await controller.stop()
    
    print("\n   Le robot a-t-il avancé vers la CAMÉRA (avant) ?")
    print("   Ou vers le RASPBERRY PI (arrière) ?")
    reponse = input("   [camera/raspberry]: ")
    
    if reponse.lower() == "raspberry":
        print("\n   ❌ Direction inversée ! On va corriger.")
    else:
        print("\n   ✅ Direction correcte !")
    
    print("\n2. Test rotation LEFT")
    await controller.move("turn_left", 0, 0, 3, 0)
    await asyncio.sleep(2)
    await controller.stop()
    
    print("\n   Le robot a tourné dans quel sens ?")
    print("   (vu du dessus, sens horaire = vers la droite)")
    sens = input("   [horaire/antihoraire]: ")

asyncio.run(test())
