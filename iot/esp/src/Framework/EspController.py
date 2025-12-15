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
        """Method to be overridden by child classes"""
        pass

    async def main(self):
        self.logger.info("Starting EspController main loop")
        
        if not self.wifi_manager.connect():
            self.logger.error("Failed to connect to WiFi")
            return
        
        self.logger.info("WiFi connected successfully")
        
        if not await self.websocket_client.connect():
            self.logger.error("Failed to connect to WebSocket")
            return
        
        self.logger.info("WebSocket connected successfully")
        
        listener_task = asyncio.create_task(
            self.websocket_client.listen(self.process_message)
        )
        
        counter = 0
        while True:
            await asyncio.sleep(self.config.heartbeat_interval)
            counter += 1
            
            heartbeat_message = json.dumps({
                "type": "heartbeat", 
                "counter": counter,
                "device_id": self.config.device_id
            })
            
            await self.websocket_client.send(heartbeat_message)
            self.logger.debug(f"Sent heartbeat: {counter}")

    def cleanup(self):
        self.logger.info("Cleaning up resources")
        self.websocket_client.close()
        # self.wifi_manager.disconnect()
        self.logger.info("Cleanup completed")
