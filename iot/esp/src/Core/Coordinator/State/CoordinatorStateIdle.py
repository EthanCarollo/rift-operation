import uasyncio as asyncio
from src.Core.Coordinator.CoordinatorState import CoordinatorState
import src.Core.Coordinator.CoordinatorConstants as CC

class CoordinatorStateIdle(CoordinatorState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = CC.CoordinatorSteps.IDLE

    async def enter(self):
        self.workshop.logger.info("Entering IDLE state")

    async def handle_button(self, button_index):
        self.workshop.logger.info(f"Button {button_index} pressed in IDLE")
        # Example logic: if button 1 is pressed, maybe move to ACTIVE, or just log for now
