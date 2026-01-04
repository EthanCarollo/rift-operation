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
        
        if role == "nightmare":
            self.workshop.logger.info("Futur implementation : Allumage des Leds du Hibou")
            self.workshop.logger.info("State: LIGHT -> Waiting for button press (Simulating Light Sensor)")
        else:
            self.workshop.logger.info("State: LIGHT -> Waiting for Nightmare Light Sensor signal...")

    async def handle_button(self):
        # Only Nightmare handles the light sensor button
        if self.workshop.hardware.role != "nightmare":
            return

        if not self.light_triggered:
            self.light_triggered = True
            self.workshop.logger.info("Button pressed -> Light triggered")
            self.workshop.logger.info("Futur implementation : Changement Mapping Video")
            # Send signal to sync with Dream via JSON payload
            device_id = self.workshop.controller.config.device_id
            await self.workshop.send_rift_json(lost_mp3_play="identify_monster.mp3", lost_light_is_triggered=True, lost_video_play="video2.mp4", device_id=device_id)

    async def handle_message(self, payload):
        if payload.get("lost_light_is_triggered") is True:
             if not self.light_triggered: # Prevent double trigger logic if needed, though handle_button sets it too. 
                 self.light_triggered = True
                 self.workshop.logger.info("Light Sensor Triggered")
                 # Auto transition to Cage
                 await self.next_step()

    async def next_step(self):
        from src.Core.Lost.State.LostStateCage import LostStateCage
        await self.workshop.swap_state(LostStateCage(self.workshop))
