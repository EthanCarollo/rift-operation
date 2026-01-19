from src.Framework.Controller.AbstractController import AbstractController
from src.Framework.Logger.Logger import Logger
from src.Core.Operator.OperatorWorkshop import OperatorWorkshop
from src.Core.Operator.OperatorHardware import OperatorHardware

class OperatorController(AbstractController):
    def __init__(self):
        super().__init__()
        self.logger = Logger("Operator", context=self)
        self.workshop = OperatorWorkshop(self)
        self.hardware = OperatorHardware(self)
        self.workshop.attach_hardware(self.hardware)

    def on_connect(self):
        self.logger.info("Connected to WebSocket")

    def on_disconnect(self):
        self.logger.info("Disconnected from WebSocket")

    async def on_message(self, message):
        await self.workshop.process_message(message)

    async def run_loop(self):
        # Hardware update loop
        self.hardware.update()
