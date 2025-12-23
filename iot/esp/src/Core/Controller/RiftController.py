"""
RiftController - Universal Controller for the RIFT workshop (ESP32 & Raspberry Pi)
"""
import sys

# --- PLATFORM SELECTION ---
# Uncomment the section corresponding to your hardware

# from src.Framework.EspController import EspController as BaseController
# from src.Core.Rift.RiftHardware import RiftHardware as Hardware
from src.Framework.PiController import PiController as BaseController
from src.Core.Rift.RiftHardwarePi import RiftHardwarePi as HardwareRaspberry

from src.Core.Rift.RiftWorkshop import RiftWorkshop

class RiftController(BaseController):
    """RIFT workshop controller"""

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "RiftController"
        
        # Workshop handles state machine
        self.workshop = RiftWorkshop(self)
        # Hardware handles RFID readers
        # self.hardware = Hardware(self)
        self.hardware = HardwareRaspberry(self)
        
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
