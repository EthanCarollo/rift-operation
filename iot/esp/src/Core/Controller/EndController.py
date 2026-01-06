import ujson as json
from src.Framework.EspController import EspController
from src.Framework.Button.Button import Button
from src.Core.Stranger.StrangerWebSocketButtonDelegate import StrangerWebSocketButtonDelegate
from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
from src.Framework.Config import Config

class EndController(EspController):
    def __init__(self, config: Config):
        super().__init__(config, "EndController")
        # self.logger.name = "EndController"


    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            # Handle it
        except Exception as e:
            # Temporary disable that
            pass

    async def update(self):
        pass