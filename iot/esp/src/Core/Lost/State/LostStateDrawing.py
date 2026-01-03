"""
LostStateDrawing.py - Drawing state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateDrawing(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DRAWING

    async def enter(self):
        self.workshop.logger.info("State: DRAWING -> Waiting for App Recognition")

    async def exit(self):
        pass

    async def handle_message(self, payload):
        recognized = payload.get("lost_drawing_recognized")
        
        if recognized is True:
            self.workshop.logger.info("Audio: Drawing Success")
            await self.workshop.send_rift_json(torch=True, lost_mp3_play="drawing_success.mp3")
            await self.next_step()
            
        elif recognized is False:
            # Play Error Sound
            self.workshop.logger.info("Audio: Drawing Error")
            await self.workshop.send_rift_json(lost_mp3_play="drawing_error.mp3")

    async def next_step(self):
        from src.Core.Lost.State.LostStateLight import LostStateLight
        await self.workshop.swap_state(LostStateLight(self.workshop))