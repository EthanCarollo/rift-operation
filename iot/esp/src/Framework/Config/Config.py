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
    def __init__(self, wifi=None, websocket=None, depth=None, device_id="ESP32_DEFAULT", 
                 debug_mode=False, heartbeat_interval=10):
        self.wifi = wifi if wifi else WifiConfig()
        self.websocket = websocket if websocket else WebsocketConfig()
        self.depth = depth if depth else DepthConfig()
        self.device_id = device_id
        self.debug_mode = debug_mode
        self.heartbeat_interval = heartbeat_interval
        
class DepthConfig:
    def __init__(self, role="child", button_pins=None, led_pins=None, partitions=None):
        self.role = role
        self.button_pins = button_pins or {1: 14, 2: 19, 3: 23}
        self.led_pins = led_pins or {1: 25, 2: 32, 3: 33}
        self.partitions = partitions or {
            1: [1, 2, 1, 3],
            2: [3, 3, 1],
            3: [2, 1, 2, 3]
        }