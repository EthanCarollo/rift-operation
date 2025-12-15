import libs.uwebsockets.client
import uasyncio as asyncio
import ujson as json
import gc

class WebSocketClient:
    def __init__(self, config, logger=None):
        self.config = config
        self.websocket = None
        self.logger = logger

    async def connect(self):
        if self.logger:
            self.logger.info(f"Connecting to WebSocket: {self.config.server}{self.config.path}")
        
        try:
            gc.collect()
            if self.logger:
                self.logger.debug(f"Free memory before connection: {gc.mem_free()}")
            
            self.websocket = libs.uwebsockets.client.connect(self.config.server + self.config.path)
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
                # IMPORTANT: The reconnect condition fix I made:
                if self.websocket is None or not self.websocket.open:
                    if self.logger:
                        self.logger.warning("WebSocket connection lost, attempting to reconnect...")
                    if await self.connect():
                        continue
                    else:
                        await asyncio.sleep(self.config.reconnect_delay)
                        continue
                
                # Non-blocking receive for async loop
                # The underlying library might be blocking, but usually asyncio wraps it or we rely on uasyncio compatibility
                # Actually, in the original code it was: message = await self.websocket.recv()
                # Assuming libs.uwebsockets.client.connect returns a socket wrapped for async if the lib supports it, 
                # OR we just rely on the fact it was working before (except for the loop bug).
                # But wait, step 115 view of original file showed: message = await self.websocket.recv()
                # So I will restore that.
                
                message = await self.websocket.recv()
                if self.logger:
                    self.logger.debug(f"WebSocket received: {message}")
                await callback(message)
        except Exception as e:
            if self.logger:
                self.logger.error(f"WebSocket listener error: {e}")
            self.websocket = None

    async def send(self, message):
        if self.websocket is not None and self.websocket.open:
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