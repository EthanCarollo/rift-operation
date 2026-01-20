from src.Core.Operator.OperatorState import OperatorState
from src.Core.Operator import OperatorConstants as OC
import uasyncio as asyncio

class OperatorStateBattle(OperatorState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = OC.OperatorSteps.BATTLE_MODE
        self.battle_ready = False # LED state for Attack Button

    async def enter(self):
        await super().enter()
        # Initialize logic based on last payload
        if self.workshop._last_payload:
            await self.handle_message(self.workshop._last_payload)

    async def exit(self):
        # Ensure LED is off when leaving
        if self.workshop.hardware and self.workshop.hardware.battle_button:
             self.workshop.hardware.battle_button.turn_off()

    async def handle_message(self, payload):
        # 1. Check Battle State (FIGHTING, WEAKENED, CAPTURED)
        battle_state = payload.get("battle_state", "")
        
        # If Captured, we might want to switch state or just chill
        if battle_state == "CAPTURED" or battle_state == "Captured":
            # Maybe switch to Victory?
            # User said "ensuite c'est terminé pour les esp"
            pass

        # 2. Attack Button Logic (Only in FIGHTING/Normal, not Weakened?)
        # User: "on renvoie ... battle_hit_confirmed=True ... tant qu'on est dans le battle_state=Battle"
        # Assuming "Battle" means fighting.
        # Check drawings
        dream_ok = payload.get("battle_drawing_dream_recognised", False)
        nightmare_ok = payload.get("battle_drawing_nightmare_recognised", False)
        
        should_be_ready = (dream_ok and nightmare_ok) and (battle_state != "WEAKENED" and battle_state != "Weakened" and battle_state != "CAPTURED" and battle_state != "Captured")
        
        if should_be_ready and not self.battle_ready:
            self.battle_ready = True
            if self.workshop.hardware and self.workshop.hardware.battle_button:
                self.workshop.hardware.battle_button.turn_on()
        elif not should_be_ready and self.battle_ready:
             self.battle_ready = False
             if self.workshop.hardware and self.workshop.hardware.battle_button:
                self.workshop.hardware.battle_button.turn_off()

    async def handle_button(self, button_type):
        if button_type == "battle" and self.battle_ready:
            self.workshop.logger.info("Battle Hit Confirmed!")
            await self.workshop.send_json({"battle_hit_confirmed": True})
            # Optimistically turn off? Or wait for payload update?
            # User says "renvoie le meme payload ... et on fait ça en boucle"
            # If we keep it on, user might spam. Better turn off and wait for drawings to be re-confirmed?
            # Usually backend clears flags after hit. Let's keep it consistent with payload.
            # But to give feedback, maybe blink? Or just rely on payload update handling to turn it off.
            pass

    async def handle_rfid(self, uid):
        # Check if Weakened
        payload = self.workshop._last_payload
        battle_state = payload.get("battle_state", "")
        
        if battle_state == "WEAKENED" or battle_state == "Weakened":
            # Check UUID
            # For now accept any or check config
            # if uid == OC.OperatorConfig.CAGE_UUID:
             self.workshop.logger.info(f"Cage UUID Scanned: {uid} -> CAPTURE")
             await self.workshop.send_json({"battle_state": "CAPTURED"})
