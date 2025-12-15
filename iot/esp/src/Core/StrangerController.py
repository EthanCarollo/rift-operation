import ujson as json
from src.Framework.EspController import EspController

class StrangerController(EspController):
    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "StrangerController"

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
        except Exception as e:
            self.logger.error(f"Failed to parse message: {message}")