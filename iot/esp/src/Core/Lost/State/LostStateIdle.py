"""
LostStateIdle.py - Idle state
"""
from src.Core.Lost.State.LostState import LostState
import src.Core.Lost.LostConstants as LC

class LostStateIdle(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.STEP_IDLE

    async def enter(self):
        pass # Nothing to do on enter Idle usually

    async def handle_message(self, payload):
        counts = (payload.get("children_rift_part_count"), payload.get("parent_rift_part_count"))
        if counts == LC.TARGET_COUNTS:
            from src.Core.Lost.State.LostStateActive import LostStateActive
            await self.workshop.swap_state(LostStateActive(self.workshop))

    async def next_step(self):
        from src.Core.Lost.State.LostStateActive import LostStateActive
        await self.workshop.swap_state(LostStateActive(self.workshop))
