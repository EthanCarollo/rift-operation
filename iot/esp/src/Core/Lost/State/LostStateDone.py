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
        self.workshop.logger.info("State: DONE. Waiting for 'cage_is_on_monster'...")
        await self.check_condition()

    async def handle_message(self, payload):
        await self.check_condition(payload)

    async def check_condition(self, payload=None):
        data = payload if payload else self.workshop._last_payload
        if not data: return

        if data.get("cage_is_on_monster") is True:
             self.workshop.logger.info("Cage OK -> Opening Servo & Finishing")
             
             # Open Servo
             self.workshop.hardware.set_servo(90) # Open angle? Assume 90.
             await asyncio.sleep_ms(1000)
             # Send WS Finished
             await self.workshop.controller.websocket_client.send("finished")
             # Stop or Loop? User said "envoie msg fin...". DONE.
             # Maybe detach callback/stop update? For now just stay here.

    async def next_step(self):
        pass
