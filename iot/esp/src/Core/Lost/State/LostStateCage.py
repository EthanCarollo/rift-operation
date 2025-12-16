"""
LostStateCage.py - Cage state
"""
import uasyncio as asyncio
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateCage(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_CAGE

    async def enter(self):
        self.workshop.logger.log_event("child", "cage", "rfid", "DETECTED: CAGE_A")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("child", "cage", "rfid", "CORRECT")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        await self.workshop.send_rift_json(cage=True)
        await asyncio.sleep_ms(self.workshop.current_step_delay)

    async def next_step(self):
        from src.Core.Lost.State.LostStateDone import LostStateDone
        await self.workshop.swap_state(LostStateDone(self.workshop))
