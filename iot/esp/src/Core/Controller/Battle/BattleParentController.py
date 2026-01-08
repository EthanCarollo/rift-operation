"""
BattleParentController - ESP32 Controller for the BATTLE workshop (Parent Role)

State Machine:
    IDLE -> APPEARING -> FIGHTING (x5) -> HIT (x5) -> WEAKENED -> CAPTURED -> DONE

Hardware:
    - LED Strip (WS2812B) - Blue color
    - RFID Reader (cage detection)
    - Arcade Button with LED
"""
import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Core.Battle.BattleWorkshop import BattleWorkshop
from src.Core.Battle.BattleHardware import BattleHardware


class BattleParentController(EspController):
    """BATTLE workshop controller - Parent Role (Blue)"""

    def __init__(self, config):
        super().__init__(config, "BattleParentController")
        
        # Instantiate Workshop and Hardware
        self.workshop = BattleWorkshop(self)
        self.hardware = BattleHardware(config, self, role="parent")
        
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
