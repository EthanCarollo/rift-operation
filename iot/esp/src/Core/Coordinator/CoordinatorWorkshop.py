import uasyncio as asyncio
import src.Core.Coordinator.CoordinatorConstants as CC
from src.Core.Coordinator.State.CoordinatorStateIdle import CoordinatorStateIdle

class CoordinatorWorkshop:
    def __init__(self, controller):
        self.controller = controller
        self.logger = controller.logger # Use controller's logger directly for now or wrap if needed
        self.hardware = None
        self.state = None
        
        # Initialize State
        asyncio.create_task(self.swap_state(CoordinatorStateIdle(self)))

    def attach_hardware(self, hardware):
        self.hardware = hardware

    def on_button_event(self, button_index):
        if self.state:
            asyncio.create_task(self.state.handle_button(button_index))

    async def swap_state(self, new_state):
        try:
            old_step = self.state.step_id if self.state else -1
            
            if self.state:
                await self.state.exit()
                
            self.state = new_state
            
            # Simple logging of transition
            self.logger.info(f"Transition: {CC.CoordinatorSteps.get_name(old_step)} -> {CC.CoordinatorSteps.get_name(self.state.step_id)}")
            
            await self.state.enter()
        except Exception as e:
            self.controller.logger.error(f"Error in swap_state: {e}")

    async def process_message(self, message: str):
        # Handle messages if needed
        if self.state:
            await self.state.handle_message(message)

    async def reset(self):
        self.logger.info("Coordinator workshop reset")
        await self.swap_state(CoordinatorStateIdle(self))
