import os

# WebSocket Server Configuration
# Default to the production server, but allow override via environment variable
DEFAULT_WS_URI = "ws://server.riftoperation.ethan-folio.fr/ws"
WS_SERVER_URI = os.getenv("WS_SERVER_URI", DEFAULT_WS_URI)
