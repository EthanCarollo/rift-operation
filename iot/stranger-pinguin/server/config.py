import os

# WebSocket Server Configuration
# Default to the production server, but allow override via environment variable
DEFAULT_WS_URI = "ws://192.168.10.7:8000/ws"
WS_SERVER_URI = os.getenv("WS_SERVER_URI", DEFAULT_WS_URI)

# Dual Server Configuration
COSMO_PORT = 8000
DARK_COSMO_PORT = 8001

# Audio Map Paths
COSMO_AUDIO_MAP = "audio_map.json"
DARK_COSMO_AUDIO_MAP = "dark_audio_map.json"

# Server Mode Device IDs
COSMO_DEVICE_ID = "cosmo-server"
DARK_COSMO_DEVICE_ID = "dark-cosmo-server"

# Step Triggers (when to activate/deactivate)
# Cosmo: activates on step_3, deactivates on step_4
COSMO_ACTIVATE_STEP = "step_3"
COSMO_DEACTIVATE_STEP = "step_4"

# Dark Cosmo: activates on step_2, deactivates on step_3
DARK_COSMO_ACTIVATE_STEP = "step_2"
DARK_COSMO_DEACTIVATE_STEP = "step_3"

# Dark Cosmo Detection Audio (played on Cosmo when is_dark_cosmo_here == true)
DARK_COSMO_DETECTED_AUDIO = "dark_cosmo_detected.json"
