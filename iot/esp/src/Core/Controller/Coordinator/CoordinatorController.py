import uasyncio as asyncio
from src.Framework.EspController import EspController
from src.Core.Coordinator.CoordinatorWorkshop import CoordinatorWorkshop
from src.Core.Coordinator.CoordinatorHardware import CoordinatorHardware

class CoordinatorController(EspController):
    """Coordinator Controller - Manages 3 buttons and RVR"""

    def __init__(self, config):
        super().__init__(config, "CoordinatorController")
        
        # Instantiate Workshop and Hardware
        self.workshop = CoordinatorWorkshop(self)
        self.hardware = CoordinatorHardware(config, self)
        
        # Setup Links
        self.workshop.attach_hardware(self.hardware)
        self.hardware.attach_callback(self.workshop)

    async def update(self):
        """Main loop callback"""
        self.hardware.update()

    async def process_message(self, message: str):
        """Delegate WebSocket messages to Workshop"""
        await self.workshop.process_message(message)

    async def reset(self):
        """Delegate reset to Workshop"""
        await self.workshop.reset()
