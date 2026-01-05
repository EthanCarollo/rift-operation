import gc
import uasyncio as asyncio
import ujson as json
from src.Framework.WifiManager import WifiManager
from src.Framework.WebSocketClient import WebSocketClient
from src.Framework.Logger import Logger
from src.Framework.Config import Config
from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData

class EspController:
    def __init__(self, config: Config):
        self.config: Config = config
        self.logger = Logger("EspController", Logger.LOG_LEVEL_INFO, esp32_mode=True, max_log_size=500)
        self.wifi_manager = WifiManager(config.wifi.ssid, config.wifi.password, self.logger)
        self.websocket_client: WebSocketClient = WebSocketClient(config.websocket, self.logger)

        if config.debug_mode:
            self.logger.set_level(Logger.LOG_LEVEL_DEBUG)
            self.logger.info("Debug mode enabled")

    async def process_message(self, message):
        if message is None : 
            return
        try:
            data = json.loads(message)
            self.logger.info("Received message: {}".format(data))

            if data.get("cmd") == "ping":
                await self.websocket_client.send(json.dumps({"cmd": "pong"}))

        except Exception as e:
            self.logger.error("Failed to process message: {}".format(e))

    async def main(self):
        self.logger.info("Starting EspController main loop")

        if not self.wifi_manager.connect():
            self.logger.error("Failed to connect to WiFi")
            return

        if not await self.websocket_client.connect():
            self.logger.error("Failed to connect to WebSocket")
            return

        asyncio.create_task(
            self.websocket_client.listen(self.process_message)
        )

        # Removed: await self.presence() - ESP now only sends when it has data to send

        while True:
            try:
                await self.update()
                await asyncio.sleep(0.02)
            except Exception as e:
                self.logger.error("Error in main loop: {}".format(e))
                await asyncio.sleep(1)



    async def presence(self):
        await self.websocket_client.send(RiftOperationJsonData(device_id= self.config.device_id).to_json())

    async def update(self):
        raise NotImplementedError

    def cleanup(self):
        self.websocket_client.close()
