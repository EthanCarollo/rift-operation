"""
RiftController - ESP32 Controller for the RIFT workshop

Handles 3 Dream RFID readers (3 Nightmare later).
Uses RiftWorkshop for state-based logic.
"""

from src.Framework.EspController import EspController
from src.Core.Rift.RiftWorkshop import RiftWorkshop
from src.Core.Rift.RiftHardware import RiftHardware

class RiftController(EspController):
    """RIFT workshop controller"""

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "RiftController"
        
        # Workshop handles state machine
        self.workshop = RiftWorkshop(self)
        # Hardware handles RFID readers
        self.hardware = RiftHardware(self)
        # Link them together
        self.hardware.attach_workshop(self.workshop)
        self.workshop.attach_hardware(self.hardware)
        
        # Initialize state
        self.workshop.init_state()
        self.logger.info("RiftController initialized")

    async def update(self):
        """Main loop callback - poll RFID readers"""
        self.hardware.update()

    async def process_message(self, message: str):
        """Delegate WebSocket messages to Workshop"""
        await self.workshop.process_message(message)

    async def reset(self):
        """Delegate reset to Workshop"""
        await self.workshop.reset()
