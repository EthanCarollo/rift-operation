"""WebSocket client for Rift Operation server."""

import ssl
import json
import threading
import websocket

# Server URL
WS_URL = "ws://server.riftoperation.ethan-folio.fr/ws"

class RiftWebSocket:
    """WebSocket client for Rift Operation battle server."""
    
    def __init__(self, url: str = WS_URL):
        self.url = url
        self.ws = None
        self.connected = False
        self.last_state = {}
        self._on_connect = None
        self._on_disconnect = None
    
    def connect(self, on_connect=None, on_disconnect=None):
        """Connect to WebSocket server in background thread."""
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        
        def on_open(ws):
            self.connected = True
            if self._on_connect:
                self._on_connect()
        
        def on_message(ws, message):
            try:
                self.last_state = json.loads(message)
            except json.JSONDecodeError:
                pass
        
        def on_close(ws, *args):
            self.connected = False
            if self._on_disconnect:
                self._on_disconnect()
        
        def on_error(ws, error):
            print(f"WS Error: {error}")
        
        # Skip SSL verification for self-signed certs
        ssl_opts = {"cert_reqs": ssl.CERT_NONE}
        
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error
        )
        
        thread = threading.Thread(
            target=lambda: self.ws.run_forever(sslopt=ssl_opts),
            daemon=True
        )
        thread.start()
    
    def send_image(self, image_base64: str, role: str, extra_data: dict = None):
        """Send transformed image to server."""
        if not self.connected or not self.ws:
            return False
        
        try:
            payload = self.last_state.copy()
            payload["device_id"] = "battle-camera"
            
            data_url = f"data:image/png;base64,{image_base64}"
            
            if role == "dream":
                payload["battle_drawing_dream_image"] = data_url
            else:
                payload["battle_drawing_nightmare_image"] = data_url
            
            # Merge extra data (like recognition flags)
            if extra_data:
                payload.update(extra_data)
            
            self.ws.send(json.dumps(payload))
            return True
        
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def close(self):
        """Close WebSocket connection."""
        if self.ws:
            self.ws.close()
