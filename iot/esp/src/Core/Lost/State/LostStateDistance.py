"""
LostStateDistance.py - Distance state
"""
import uasyncio as asyncio
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateDistance(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_DISTANCE

    async def enter(self):
        self.workshop.logger.log_event("child", "distance_sensor", "sensor", "TRIGGERED")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("child", "llm", "ia", "TRIGGERED")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("child", "speaker", "audio", "ON")

    async def next_step(self):
        from src.Core.Lost.State.LostStateDrawing import LostStateDrawing
        await self.workshop.swap_state(LostStateDrawing(self.workshop))
