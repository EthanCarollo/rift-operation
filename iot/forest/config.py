# --- Debug ---
DEBUG = True  # Set to False to reduce serial output

# --- Wi-Fi ---
WIFI_SSID = "Cudy-FA5C"
WIFI_PASS = "58448069"

# --- WebSocket ---
WS_URL = "ws://172.28.55.66:3000/ws"

# --- Protocol options ---
SEND_HELLO_ON_CONNECT = True

# --- Device identity ---
DEVICE_ID = "esp32-forest-01"
WORKSHOP = "forest"
ROLE = "child"

# --- Workshop activation ---
# Example server message: {"type":"workshop", "value":{"name":"forest","action":"start"}}
ACTIVATE_TYPE = "workshop"
ACTIVATE_NAME = "forest"

# --- Heartbeat ---
# 0 = disabled
HEARTBEAT_MS = 0

# --- Inputs ---
PIN_BUTTON = 27
DEBOUNCE_MS = 250

# Button interactions
LONG_PRESS_MS = 1200

# --- Small config objects ---
class WifiConfig:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password

class WebsocketConfig:
    def __init__(self, url):
        self.url = url

class DeviceConfig:
    def __init__(self, device_id, workshop, role):
        self.device_id = device_id
        self.workshop = workshop
        self.role = role


WIFI_CONFIG = WifiConfig(WIFI_SSID, WIFI_PASS)
WS_CONFIG = WebsocketConfig(WS_URL)
DEVICE_CONFIG = DeviceConfig(DEVICE_ID, WORKSHOP, ROLE)