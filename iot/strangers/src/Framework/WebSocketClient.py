import uwebsocket
import uasyncio as asyncio
import ujson as json

class WebSocketClient:
    def __init__(self, config):
        self.config = config
        self.websocket = None

    async def connect(self):
        try:
            self.websocket = await uwebsocket.connect(self.config.server + self.config.path)
            return True
        except Exception as e:
            return False

    async def listen(self, callback):
        try:
            while True:
                if self.websocket is None or self.websocket.closed:
                    if await self.connect():
                        continue
                    else:
                        await asyncio.sleep(5)
                        continue
                
                message = await self.websocket.recv()
                await callback(message)
        except Exception as e:
            self.websocket = None

    async def send(self, message):
        if self.websocket is not None and not self.websocket.closed:
            try:
                await self.websocket.send(message)
            except Exception as e:
                self.websocket = None

    def close(self):
        if self.websocket is not None:
            self.websocket.close()
            self.websocket = None