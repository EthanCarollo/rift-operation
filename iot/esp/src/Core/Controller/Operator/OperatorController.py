from src.Framework.EspController import EspController
from src.Framework.Logger.Logger import Logger
from src.Core.Operator.OperatorWorkshop import OperatorWorkshop
from src.Core.Operator.OperatorHardware import OperatorHardware

class OperatorController(EspController):
    def __init__(self, config):
        super().__init__(config, "OperatorController")
        # self.logger is already created by EspController with context "OperatorController" if we pass that name?
        # EspController init: self.logger = Logger(logger_name, ...)
        # So we don't need to recreate self.logger unless we want context?
        # EspController creates logger with name.
        
        self.workshop = OperatorWorkshop(self)
        self.hardware = OperatorHardware(self)
        self.workshop.attach_hardware(self.hardware)

    async def process_message(self, message):
        await self.workshop.process_message(message)

    async def update(self):
        # Hardware update loop
        self.hardware.update()
