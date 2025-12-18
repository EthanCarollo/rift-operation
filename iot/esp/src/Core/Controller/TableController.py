import ujson as json
import asyncio
from src.Framework.EspController import EspController
from src.Framework.Button.Button import Button
from src.Framework.Button.ButtonDelegate import ButtonDelegate
from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData
from src.Framework.Config import Config

# This is only for debugging

class PartCountDelegate(ButtonDelegate):
    def __init__(self, controller, dream_count, nightmare_count):
        self.controller = controller
        self.dream_count = dream_count
        self.nightmare_count = nightmare_count

    def on_click(self):
        asyncio.create_task(self.send_counts())

    async def send_counts(self):
        try:
            json_data = RiftOperationJsonData(
                device_id=self.controller.config.device_id,
                dream_rift_part_count=self.dream_count,
                nightmare_rift_part_count=self.nightmare_count
            )
            await self.controller.websocket_client.send(json_data.to_json())
        except Exception as e:
            self.controller.logger.error(f"Failed to send part counts: {e}")

class TableController(EspController):
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger.name = "TableController"

        # Initialize buttons with example values (1, 1) as requested
        self.button_5 = Button(5, PartCountDelegate(self, 1, 1))
        self.button_18 = Button(18, PartCountDelegate(self, 2, 2))
        self.button_19 = Button(19, PartCountDelegate(self, 3, 3))

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