"""
LostStateIdle.py - Idle state
"""
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateIdle(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.IDLE

    async def enter(self):
        device_id = self.workshop.controller.config.device_id
        self.workshop.logger.info(f"{device_id} : Etat Idle")

    async def handle_message(self, payload):
        counts = (payload.get("children_rift_part_count"), payload.get("parent_rift_part_count"))
        if counts != LC.LostGameConfig.TARGET_COUNTS:
            return

        role = self.workshop.hardware.role
        
        if role == "child":
            # Just wait for start signal
            device_id = self.workshop.controller.config.device_id
            self.workshop.logger.info(f"WebSocket sent. {device_id} : Active")
            await self.workshop.controller.websocket_client.send("active")
            
            from src.Core.Lost.State.LostStateDistance import LostStateDistance
            await self.workshop.swap_state(LostStateDistance(self.workshop))

        elif role == "parent":
            # Check torch_scanned
            if payload.get("torch_scanned") is True:
                device_id = self.workshop.controller.config.device_id
                self.workshop.logger.info(f"WebSocket sent. {device_id} : Active")
                await self.workshop.controller.websocket_client.send("active")
                from src.Core.Lost.State.LostStateLight import LostStateLight
                await self.workshop.swap_state(LostStateLight(self.workshop))