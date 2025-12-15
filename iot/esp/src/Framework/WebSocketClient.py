import libs.uwebsockets.client
import uasyncio as asyncio
import ujson as json
import gc
import sys

class WebSocketClient:
    def __init__(self, config, logger=None):
        self.config = config
        self.websocket = None
        self.logger = logger

    async def connect(self):
        if self.logger:
            self.logger.info(f"Connecting to WebSocket: {self.config.server}{self.config.path}")

        # Yield to allow other tasks to process and release resources
        await asyncio.sleep(0.1)
        gc.collect()

        if self.logger:
            self.logger.debug(f"Free memory before connection: {gc.mem_free()}")

        try:
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
                sys.print_exception(e)

            # Ensure minimal cleanup if partial connection occurred
            if self.websocket:
                try:
                    self.websocket.close()
                except:
                    pass
            self.websocket = None
            
            # Reclaim memory immediately after failure
            gc.collect()
            return False

    async def listen(self, callback):
        if self.logger:
            self.logger.info("Starting WebSocket listener")

        while True:
            try:
                if self.websocket is None or not self.websocket.open:
                    if self.logger:
                        self.logger.warning("WebSocket disconnected, reconnecting...")
                    
                    # Wait before reconnecting to avoid thrashing
                    await asyncio.sleep(self.config.reconnect_delay)
                    
                    if not await self.connect():
                        continue

                try:
                    message = self.websocket.recv()
                    if message is not None and message != "":
                        if self.logger:
                            self.logger.debug(f"WebSocket received: {message}")
                        await callback(message)
                except OSError as e:
                    # ESP32 raises OSError: [Errno 11] EAGAIN when no data is available on a non-blocking socket
                    pass
                except Exception as inner_e:
                    if self.logger:
                        self.logger.error(f"Error receiving message: {inner_e}")
                    raise inner_e

                await asyncio.sleep_ms(10) # Small yield to prevent CPU hogging

                # Periodically collect garbage to prevent fragmentation
                if gc.mem_free() < 12000:
                    gc.collect()

            except Exception as e:
                if self.logger:
                    self.logger.error(f"WebSocket listen error: {e}")
                
                # Close explicitly to free socket resources
                self.close()
                
                gc.collect()
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
                self.close()
        else:
            if self.logger:
                self.logger.warning("WebSocket not connected, cannot send message")

    def close(self):
        if self.websocket is not None:
            if self.logger:
                self.logger.info("Closing WebSocket connection")
            try:
                self.websocket.close()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error closing socket: {e}")
            self.websocket = None
            gc.collect()
            if self.logger:
                self.logger.info("WebSocket connection closed")
