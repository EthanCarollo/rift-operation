"""
LostController - ESP32 Controller for the LOST workshop

State Machine:
    IDLE -> ACTIVE -> DISTANCE -> DRAWING -> LIGHT -> CAGE -> DONE

Triggers:
    - Auto-starts when receiving JSON with children=2, parent=2
    - Button press advances to next step
"""

import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Core.Lost.LostWorkshop import LostWorkshop
from src.Framework.Button.Button import Button
from src.Core.Lost.LostButtonDelegate import LostButtonDelegate
from src.Core.Lost.LostHardware import LostHardware


class LostController(EspController):
    """LOST workshop controller - wrapper for LostWorkshop"""

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"
        
        # Instantiate Workshop business logic
        self.workshop = LostWorkshop(self)
        
        # Instantiate Hardware
        self.hardware = LostHardware(config, self)
        
        # Setup Links
        self.workshop.attach_hardware(self.hardware)
        self.hardware.attach_callback(self.workshop)
        
        self.button = Button(pin_id=27, delegate=LostButtonDelegate(self))

    async def update(self):
        """Main loop callback"""
        self.hardware.update()

    async def process_message(self, message: str):
        """Delegate WebSocket messages to Workshop"""
        await self.workshop.process_message(message)

    async def handle_short_press(self):
        """Delegate button press to Workshop"""
        await self.workshop.handle_short_press()

    async def reset(self):
        """Delegate reset to Workshop"""
        await self.workshop.reset()