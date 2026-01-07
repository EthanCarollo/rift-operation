import ujson as json
from src.Framework.EspController import EspController
from src.Framework.Config import Config

"""
Here we will need to put new led light for this kind of shit
"""
class RiftLedController(EspController):
    def __init__(self, config: Config):
        super().__init__(config, "RiftLedController")


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