"""
LostController - ESP32 Controller for the LOST workshop

State Machine:
    IDLE -> INTERNE STEPS -> DONE

Triggers:
    - Auto-starts when receiving JSON with counts
"""

import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Core.Lost.LostWorkshop import LostWorkshop
from src.Core.Lost.LostHardware import LostHardware


class LostController(EspController):
    """LOST workshop controller - wrapper for LostWorkshop"""

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"
        # Instantiate Workshop and Hardware
        self.workshop = LostWorkshop(self)
        self.hardware = LostHardware(config, self)
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