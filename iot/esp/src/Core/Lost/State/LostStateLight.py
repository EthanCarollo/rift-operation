"""
LostStateLight.py - Light state
"""
import uasyncio as asyncio
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateLight(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_LIGHT

    async def enter(self):
        self.workshop.logger.log_event("parent", "light_sensor", "sensor", "TRIGGERED")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("parent", "mapping_video", "video", "SWITCH: reveal")

    async def next_step(self):
        from src.Core.Lost.State.LostStateCage import LostStateCage
        await self.workshop.swap_state(LostStateCage(self.workshop))
