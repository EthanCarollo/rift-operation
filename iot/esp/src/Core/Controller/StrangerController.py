import ujson as json
from src.Framework.EspController import EspController
from src.Framework.Button.Button import Button
from src.Core.Stranger.StrangersWebSocketButtonDelegate import StrangersWebSocketButtonDelegate

class StrangerController(EspController):
    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "StrangerController"

        self.button = Button(17, StrangersWebSocketButtonDelegate(self))

    async def process_message(self, message):
        if message is None :
            return
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
        except Exception as e:
            self.logger.error(f"Failed to parse message: {message}")

    async def update(self):
        print("update called")