"""
LostStateIdle.py - Idle state
"""
import ujson as json
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateIdle(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.IDLE

    async def enter(self):
        device_id = self.workshop.controller.config.device_id
        self.workshop.logger.info(f"{device_id} : Etat Idle")
        # Reset servo to 0° for a new workshop
        self.workshop.hardware.set_servo(0)

    async def handle_message(self, payload):
        # Trigger condition: rift_part_count == 2
        if payload.get("rift_part_count") == 2:
            device_id = self.workshop.controller.config.device_id
            # Send activation confirmation + Start Video 1
            await self.workshop.send_rift_json(
                lost_state="active", 
                rift_part_count=2, 
                lost_video_play="video1.mp4",
                device_id=device_id
            )
            await self.next_step()

    async def next_step(self):
        from src.Core.Lost.State.LostStateLight import LostStateLight
        await self.workshop.swap_state(LostStateLight(self.workshop))