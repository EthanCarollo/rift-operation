import uwebsockets.client as websockets
import uasyncio as asyncio
import ujson as json

class WebSocketClient:
    def __init__(self, config, logger=None):
        self.config = config
        self.websocket = None
        self.logger = logger

    async def connect(self):
        if self.logger:
            self.logger.info(f"Connecting to WebSocket: {self.config.server}{self.config.path}")
        
        try:
            self.websocket = await websockets.connect(self.config.server + self.config.path)
            if self.logger:
                self.logger.info("WebSocket connected successfully")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to connect to WebSocket: {e}")
            return False

    async def listen(self, callback):
        if self.logger:
            self.logger.info("Starting WebSocket listener")
        
        try:
            while True:
                if self.websocket is None or self.websocket.closed:
                    if self.logger:
                        self.logger.warning("WebSocket connection lost, attempting to reconnect...")
                    if await self.connect():
                        continue
                    else:
                        await asyncio.sleep(self.config.reconnect_delay)
                        continue
                
                message = await self.websocket.recv()
                if self.logger:
                    self.logger.debug(f"WebSocket received: {message}")
                await callback(message)
        except Exception as e:
            if self.logger:
                self.logger.error(f"WebSocket listener error: {e}")
            self.websocket = None

    async def send(self, message):
        if self.websocket is not None and not self.websocket.closed:
            try:
                await self.websocket.send(message)
                if self.logger:
                    self.logger.debug(f"WebSocket sent: {message}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to send WebSocket message: {e}")
                self.websocket = None
        else:
            if self.logger:
                self.logger.warning("WebSocket not connected, cannot send message")

    def close(self):
        if self.websocket is not None:
            if self.logger:
                self.logger.info("Closing WebSocket connection")
            self.websocket.close()
            self.websocket = None
            if self.logger:
                self.logger.info("WebSocket connection closed")