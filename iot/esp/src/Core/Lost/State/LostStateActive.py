"""
LostStateActive.py - Active state (Start sequence)
"""
import uasyncio as asyncio
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateActive(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_ACTIVE

    async def enter(self):
        self.workshop.logger.logger.info("LOST Started")
        await self.workshop.send_rift_json(preset=True)
        
        await asyncio.sleep_ms(LC.START_DELAY)
        self.workshop.logger.log_event("system", "workshop", "start", "ON")
        await asyncio.sleep_ms(LC.START_DELAY)
        self.workshop.logger.log_event("parent", "speaker", "audio", "ON")
        await asyncio.sleep_ms(LC.START_DELAY)
        self.workshop.logger.log_event("child", "animals_led", "led", "ON")

    async def next_step(self):
        from src.Core.Lost.State.LostStateDistance import LostStateDistance
        await self.workshop.swap_state(LostStateDistance(self.workshop))
