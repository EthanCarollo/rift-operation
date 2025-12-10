import gc
import uasyncio as asyncio
import ujson as json
from src.Framework.WifiManager import WifiManager
from src.Framework.WebSocketClient import WebSocketClient

class EspController:
    def __init__(self, config):
        self.config = config
        self.wifi_manager = WifiManager(config.wifi.ssid, config.wifi.password)
        self.websocket_client = WebSocketClient(config.websocket)

    async def process_message(self, message):
        try:
            data = json.loads(message)
        except Exception as e:
            pass

    async def main(self):
        if not self.wifi_manager.connect():
            return
        
        if not await self.websocket_client.connect():
            return
        
        listener_task = asyncio.create_task(
            self.websocket_client.listen(self.process_message)
        )
        
        counter = 0
        while True:
            await asyncio.sleep(self.config.heartbeat_interval)
            counter += 1
            await self.websocket_client.send(
                json.dumps({
                    "type": "heartbeat", 
                    "counter": counter,
                    "device_id": self.config.device_id
                })
            )

    def cleanup(self):
        self.websocket_client.close()
        self.wifi_manager.disconnect()