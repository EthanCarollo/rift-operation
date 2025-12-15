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

            self.websocket = libs.uwebsockets.client.connect(
                self.config.server + self.config.path
            )
            self.websocket.sock.setblocking(False)

            if self.logger:
                self.logger.info("WebSocket connected successfully")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to connect to WebSocket: {e}")
            self.websocket = None
            return False

    async def listen(self, callback):
        if self.logger:
            self.logger.info("Starting WebSocket listener")

        while True:
            try:
                if self.websocket is None or not self.websocket.open:
                    if self.logger:
                        self.logger.warning("WebSocket disconnected, reconnecting...")
                    if not await self.connect():
                        await asyncio.sleep(self.config.reconnect_delay)
                        continue

                try:
                    message = self.websocket.recv()
                    if message is not None:
                        if self.logger:
                            self.logger.debug(f"WebSocket received: {message}")
                        await callback(message)
                except OSError as e:
                    # ESP32 raises OSError: [Errno 11] EAGAIN when no data is available on a non-blocking socket
                    pass

                await asyncio.sleep_ms(0)

                if gc.mem_free() < 10_000:
                    gc.collect()

            except Exception as e:
                if self.logger:
                    self.logger.error(f"WebSocket listen error: {e}")
                self.websocket = None
                await asyncio.sleep(self.config.reconnect_delay)

    async def send(self, message):
        if self.websocket is not None and self.websocket.open:
            try:
                self.websocket.send(message)
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
