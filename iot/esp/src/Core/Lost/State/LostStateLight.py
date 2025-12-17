"""
LostStateLight.py - Light state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.State.LostState import LostState

class LostStateLight(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.LIGHT

    async def enter(self):
        self.workshop.logger.info("State: LIGHT. Waiting for button press (Simulating Light Sensor)")

    async def handle_button(self):
        self.workshop.logger.info("Button pressed -> Light triggered")
        
        # Send manual signal for synchronization
        await self.workshop.controller.websocket_client.send("light_sensor_triggered")
        
        from src.Core.Lost.State.LostStateDone import LostStateDone
        await self.workshop.swap_state(LostStateDone(self.workshop))

    async def next_step(self):
        pass
