# --- Debug ---
DEBUG = True  # Set to False to reduce serial output

# --- Wi-Fi ---
WIFI_SSID = "SFR_F48F"
WIFI_PASS = "7b2uj3mb37js72glj1e9"

# --- WebSocket ---
WS_URL = "ws://192.168.1.57:3000/ws"

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

# Button interactions
DOUBLE_PRESS_MS = 450
LONG_PRESS_MS = 1200

# --- Inputs ---
PIN_BUTTON = 27
DEBOUNCE_MS = 250