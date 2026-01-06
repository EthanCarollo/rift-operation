"""
LostStateDone.py - Done state
"""
import uasyncio as asyncio
import ujson as json
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateDone(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DONE
        self._triggered = False

    async def enter(self):
        await self.check_condition()

    async def handle_message(self, payload):
        await self.check_condition(payload)

    async def check_condition(self, payload=None):
        if self._triggered:
            return

        data = payload if payload else self.workshop._last_payload
        if not data: return

        if data.get("lost_cage_is_on_monster") is True:
             self._triggered = True
             self.workshop.logger.info("Opening Rift Trap (Servo 180° for 3s)")
             self.workshop.hardware.set_servo(180)
             await self.workshop.send_rift_json(lost_state="done")
             # Wait for global reset (handled by Workshop)
             self.workshop.logger.info("Lost Workshop done !")

    async def next_step(self):
        pass
