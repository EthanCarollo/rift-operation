"""
LostStateDistance.py - Distance state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.State.LostState import LostState

class LostStateDistance(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DISTANCE

    async def enter(self):
        self.workshop.logger.info("State: DISTANCE. Waiting for button press (Simulating Drawing recog).")

    async def handle_button(self):
        self.workshop.logger.info("Button presed -> Drawing recognized")
        from src.Core.Lost.State.LostStateDrawing import LostStateDrawing
        await self.workshop.swap_state(LostStateDrawing(self.workshop))

    async def next_step(self):
        # No auto transition, blocked on button
        pass
