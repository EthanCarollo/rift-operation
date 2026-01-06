"""
LostNightmareController - ESP32 Controller for the LOST workshop (Nightmare Role)

State Machine:
    IDLE -> INTERNE STEPS -> DONE

Triggers:
    - Auto-starts when receiving JSON with counts
"""
import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Core.Lost.LostWorkshop import LostWorkshop
from src.Core.Lost.LostHardware import LostHardware

class LostNightmareController(EspController):
    """LOST workshop controller - Nightmare Role"""

    def __init__(self, config):
        super().__init__(config, "LostNightmareController")
        # self.logger.name = "LostNightmareController"
        # Instantiate Workshop and Hardware
        self.workshop = LostWorkshop(self)
        # Explicitly pass role="nightmare"
        self.hardware = LostHardware(config, self, role="nightmare")
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
