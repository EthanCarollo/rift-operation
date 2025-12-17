"""
LostStateDone.py - Done state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateDone(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DONE

    async def enter(self):
        await self.check_condition()

    async def handle_message(self, payload):
        await self.check_condition(payload)

    async def check_condition(self, payload=None):
        data = payload if payload else self.workshop._last_payload
        if not data: return

        if data.get("cage_is_on_monster") is True:
             self.workshop.hardware.set_servo(180)
             await asyncio.sleep_ms(500)
             await self.workshop.controller.websocket_client.send("finished")
             
             # Reset to Idle to restart the loop
             await self.workshop.reset()

    async def next_step(self):
        pass
