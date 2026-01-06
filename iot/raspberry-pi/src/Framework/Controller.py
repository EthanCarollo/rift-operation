import asyncio
import ssl
import json
import logging
import websockets
from src.Framework.Config import Config
from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData

class Controller:
    def __init__(self, config: Config):
        self.config = config
        # Configure standard logging
        logging.basicConfig(
            level=logging.INFO if not config.debug_mode else logging.DEBUG,
            format='[%(name)s] [%(levelname)s] %(message)s',
        )
        self.logger = logging.getLogger("Controller")
        logging.getLogger("websockets").setLevel(logging.ERROR)
        
        self.websocket = None
        self.uri = config.websocket.server + config.websocket.path
        
        if config.debug_mode:
            self.logger.info("Debug mode enabled")

    async def connect_websocket(self):
        while True:
            try:
                self.logger.info(f"Connecting to WebSocket: {self.uri}")
                ssl_context = None
                if self.uri.startswith("wss://"):
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                async with websockets.connect(self.uri, ssl=ssl_context) as websocket:
                    self.websocket = websocket
                    self.logger.info("WebSocket connected successfully")
                    # Run listener and update loop concurrently
                    await asyncio.gather(
                        self.listen(),
                        self.main_loop()
                    )
            except Exception as e:
                self.logger.error(f"WebSocket connection failed: {e}")
                self.websocket = None
                await asyncio.sleep(5)

    async def listen(self):
        try:
            async for message in self.websocket:
                await self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket connection closed")

    async def main_loop(self):
        while self.websocket:
            if getattr(self.websocket, "closed", False) or getattr(self.websocket, "close_code", None) is not None:
                break
            try:
                await self.update()
                await asyncio.sleep(0.05)
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)

    async def process_message(self, message):
        if message is None:
            return
        try:
            data = json.loads(message)
            # Remove this log to reduce noise
            # self.logger.info(f"Received message: {data}")
            if data.get("cmd") == "ping":
                await self.send(json.dumps({"cmd": "pong"}))

        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")

    async def send(self, message):
        if self.websocket:
            await self.websocket.send(message)

    async def update(self):
        raise NotImplementedError

    async def main(self):
        await self.connect_websocket()

    # Compatibility methods to match EspController interface if needed
    @property
    def websocket_client(self):
        # Return self as it implements send()
        return self 
