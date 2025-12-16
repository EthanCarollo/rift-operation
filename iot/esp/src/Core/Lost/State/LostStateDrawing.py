"""
LostStateDrawing.py - Drawing state
"""
import uasyncio as asyncio
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateDrawing(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_DRAWING

    async def enter(self):
        self.workshop.logger.log_event("child", "drawing", "camera", "READ")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("child", "llm", "ia", "TRIGGERED")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("child", "drawing", "ia", "RECOGNIZED: flashlight")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        await self.workshop.send_rift_json(torch=True)
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("parent", "lamp", "led", "ON")

    async def next_step(self):
        from src.Core.Lost.State.LostStateLight import LostStateLight
        await self.workshop.swap_state(LostStateLight(self.workshop))
