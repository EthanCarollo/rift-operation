import uasyncio as asyncio
import src.Core.Coordinator.CoordinatorConstants as CC

class CoordinatorState:
    def __init__(self, workshop):
        self.workshop = workshop
        self.step_id = None

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def handle_button(self, button_index):
        """Handle button press (1, 2, or 3)"""
        pass

    async def handle_message(self, payload):
        pass

    async def next_step(self):
        pass
