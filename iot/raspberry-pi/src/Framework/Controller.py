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
        
        self.websockets = set()
        
        if config.debug_mode:
            self.logger.info("Debug mode enabled")

    async def MaintainConnection(self, uri, port):
        """Maintain a WebSocket connection to a specific URI"""
        while True:
            try:
                self.logger.info(f"Connecting to : {uri}")
                ssl_context = None
                if uri.startswith("wss://"):
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                async with websockets.connect(uri, ssl=ssl_context) as websocket:
                    self.websockets.add(websocket)
                    self.logger.info(f"Connected to port {port}")
                    
                    try:
                        async for message in websocket:
                            await self.process_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.warning(f"Connection lost on port {port}")
                    finally:
                        self.websockets.discard(websocket)
            
            except Exception as e:
                # self.logger.error(f"Connection failed on port {port}: {e}")
                await asyncio.sleep(5)

    async def main_loop(self):
        """Main hardware update loop"""
        self.logger.info("Starting Main Loop")
        while True:
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
            if data.get("cmd") == "ping":
                await self.send(json.dumps({"cmd": "pong"}))
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")

    async def send(self, message):
        """Broadcast message to all connected sockets"""
        if not self.websockets:
            return

        # Create tasks for sending to all sockets
        tasks = []
        for ws in self.websockets:
            tasks.append(asyncio.create_task(ws.send(message)))
        
        # We don't wait for them to finish to avoid blocking, 
        # or we could use gather if we want confirmation. 
        # Fire and forget is usually safer for broadcasting to avoid one slow client blocking others.
        # But asyncio.gather with return_exceptions=True is also good.
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def update(self):
        raise NotImplementedError

    async def main(self):
        # Derive URIs for ports 8000, 8001, 8002
        # Config has full URI: ws://192.168.10.7:8000/ws ("create_prod")
        # We need to extract the base IP.
        
        original_uri = self.config.websocket.server # e.g. ws://192.168.10.7:8000
        path = self.config.websocket.path # /ws
        
        # Simple parsing assumption: URI ends with :PORT
        # If not, we assume default 8000.
        
        # robust extraction ?
        # split by :
        parts = original_uri.split(":")
        # parts = ['ws', '//192.168.10.7', '8000']
        
        if len(parts) >= 3:
            # Reconstruct base without port
            base = f"{parts[0]}:{parts[1]}" # ws://192.168.10.7
        else:
            base = original_uri # Fallback
            
        ports = [8000, 8001, 8002]
        tasks = [self.main_loop()]
        
        for p in ports:
            uri = f"{base}:{p}{path}"
            tasks.append(self.MaintainConnection(uri, p))
            
        await asyncio.gather(*tasks)

    # Compatibility methods to match EspController interface if needed
    @property
    def websocket_client(self):
        # Return self as it implements send()
        return self 
