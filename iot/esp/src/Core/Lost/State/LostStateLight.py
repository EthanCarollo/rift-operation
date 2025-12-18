"""
LostStateLight.py - Light state
"""
import uasyncio as asyncio
import ujson as json
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateLight(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.LIGHT

    async def enter(self):
        self.light_triggered = False
        role = self.workshop.hardware.role
        
        if role == "parent":
            self.workshop.logger.info("Futur implementation : Allumage des Leds du Hibou")
            self.workshop.logger.info("State: LIGHT -> Waiting for button press (Simulating Light Sensor)")
        else:
            self.workshop.logger.info("State: LIGHT -> Waiting for Parent Light Sensor signal...")

    async def handle_button(self):
        # Only Parent handles the light sensor button
        if self.workshop.hardware.role != "parent":
            return

        if not self.light_triggered:
            self.light_triggered = True
            self.workshop.logger.info("Button pressed -> Light triggered")
            self.workshop.logger.info("Futur implementation : Changement Mapping Video")
            self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Maintenant qu'on voit le monstre qui bully ton parent, identifiez le et capturez le avec la bonne cage!\"")
            # Send signal to sync with Child
            device_id = self.workshop.controller.config.device_id
            await self.workshop.controller.websocket_client.send(json.dumps({"signal": "light_sensor_triggered", "device_id": device_id}))
            # Also self-trigger signal handling to transition
            await self.handle_signal("light_sensor_triggered")

    async def handle_signal(self, signal):
        if signal == "light_sensor_triggered":
             if not self.light_triggered:
                 self.light_triggered = True
                 self.workshop.logger.info("Signal received: Light Sensor Triggered")
                 # Auto transition to Cage
                 await self.next_step()

    async def next_step(self):
        from src.Core.Lost.State.LostStateCage import LostStateCage
        await self.workshop.swap_state(LostStateCage(self.workshop))
