class WifiConfig:
    def __init__(self, ssid="YOUR_WIFI_SSID", password="YOUR_WIFI_PASSWORD", timeout=10, auto_reconnect=True):
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect

class WebsocketConfig:
    def __init__(self, server="ws://YOUR_WEBSOCKET_SERVER_ADDRESS", path="/YOUR_WEBSOCKET_PATH", 
                 reconnect_delay=5, ping_interval=30, binary_mode=False):
        self.server = server
        self.path = path
        self.reconnect_delay = reconnect_delay
        self.ping_interval = ping_interval
        self.binary_mode = binary_mode

class Config:
    def __init__(self, wifi=None, websocket=None, device_id="ESP32_DEFAULT", 
                 debug_mode=False, heartbeat_interval=10):
        self.wifi = wifi if wifi else WifiConfig()
        self.websocket = websocket if websocket else WebsocketConfig()
        self.device_id = device_id
        self.debug_mode = debug_mode
        self.heartbeat_interval = heartbeat_interval