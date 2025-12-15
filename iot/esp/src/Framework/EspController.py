import gc
import uasyncio as asyncio
import ujson as json
from src.Framework.WifiManager import WifiManager
from src.Framework.WebSocketClient import WebSocketClient
from src.Framework.Logger import Logger

class EspController:
    def __init__(self, config):
        self.config = config
        self.logger = Logger("EspController", Logger.LOG_LEVEL_INFO, esp32_mode=True, max_log_size=500)
        self.wifi_manager = WifiManager(config.wifi.ssid, config.wifi.password, self.logger)
        self.websocket_client = WebSocketClient(config.websocket, self.logger)

        if config.debug_mode:
            self.logger.set_level(Logger.LOG_LEVEL_DEBUG)
            self.logger.info("Debug mode enabled")

    async def process_message(self, message):
        raise NotImplementedError

    async def main(self):
        self.logger.info("Starting EspController main loop")

        if not self.wifi_manager.connect():
            self.logger.error("Failed to connect to WiFi")
            return

        if not await self.websocket_client.connect():
            self.logger.error("Failed to connect to WebSocket")
            return

        counter = 0

        while True:
            print("call in while true")
            try:
                await self.update()
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error("Error in main loop: {}".format(e))
                await asyncio.sleep(1)

    async def update(self):
        raise NotImplementedError

    def cleanup(self):
        self.websocket_client.close()
