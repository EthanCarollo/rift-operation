"""
LostStateDrawing.py - Drawing state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.State.LostState import LostState

class LostStateDrawing(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DRAWING

    async def enter(self):
        self.workshop.logger.info("State: DRAWING. Sending json with value : \"torch_scanned=True\"")
        await self.workshop.send_rift_json(torch=True)
        # Auto transition to Cage
        await self.next_step()

    async def next_step(self):
        from src.Core.Lost.State.LostStateCage import LostStateCage
        await self.workshop.swap_state(LostStateCage(self.workshop))
