"""
LostStateIdle.py - Idle state
"""
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.State.LostState import LostState

class LostStateIdle(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.IDLE

    async def enter(self):
        pass # Nothing to do

    async def handle_message(self, payload):
        counts = (payload.get("children_rift_part_count"), payload.get("parent_rift_part_count"))
        if counts != LC.LostGameConfig.TARGET_COUNTS:
            return

        role = self.workshop.hardware.role
        
        if role == "child":
            # Check distance sensor
            dist = self.workshop.hardware.get_distance()
            self.workshop.logger.debug(f"Idle check. Dist: {dist}")
            
            if dist != -1 and dist < 30:
                 self.workshop.logger.info("Distance triggered -> Active")
                 await self.workshop.controller.websocket_client.send("active")
                 from src.Core.Lost.State.LostStateDistance import LostStateDistance
                 await self.workshop.swap_state(LostStateDistance(self.workshop))

        elif role == "parent":
             # Check torch_scanned
             if payload.get("torch_scanned") is True:
                 self.workshop.logger.info("Torch scanned -> Active")
                 await self.workshop.controller.websocket_client.send("active")
                 from src.Core.Lost.State.LostStateLight import LostStateLight
                 await self.workshop.swap_state(LostStateLight(self.workshop))

    async def handle_distance(self, distance):
        # Allow event-driven trigger too for child
        if self.workshop.hardware.role == "child":
             last_pl = self.workshop._last_payload
             if not last_pl: return
             
             counts = (last_pl.get("children_rift_part_count"), last_pl.get("parent_rift_part_count"))
             if counts == LC.LostGameConfig.TARGET_COUNTS and distance < 30:
                 self.workshop.logger.logger.info("Distance event -> Active")
                 await self.workshop.controller.websocket_client.send("active")
                 from src.Core.Lost.State.LostStateDistance import LostStateDistance
                 await self.workshop.swap_state(LostStateDistance(self.workshop))
