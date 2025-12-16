"""
LostStateDone.py - Done state
"""
import uasyncio as asyncio
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateDone(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_DONE

    async def enter(self):
        self.workshop.logger.log_event("child", "servo_trap", "servo", "OPEN")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("parent", "servo_trap", "servo", "OPEN")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        self.workshop.logger.log_event("system", "workshop", "state", "FINISHED")
        
        # Final JSON
        self.workshop.logger.logger.info("Workshop finished, sending final Rift JSON")
        await self.workshop.send_rift_json(torch=True, cage=True, preset=False)

    async def next_step(self):
        # Already done, maybe loop back to Idle manually if needed, or do nothing
        pass
