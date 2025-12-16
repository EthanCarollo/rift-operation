"""
DepthConfig.py - Dedicated configuration for DEPTH workshop
"""
from src.Framework.Config.Config import WifiConfig, WebsocketConfig

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

class Config:
    def __init__(self, role="child", wifi=None, websocket=None, device_id="DEPTH_ESP"):
        self.wifi = wifi if wifi else WifiConfig()
        self.websocket = websocket if websocket else WebsocketConfig()
        self.depth = DepthConfig(role=role)
        self.device_id = device_id
        self.debug_mode = True
        self.heartbeat_interval = 15

class DepthConfigFactory:
    @staticmethod
    def create_default_child():
        return Config(
            role="child",
            device_id="DEPTH-CUDY-ESP",
            wifi=WifiConfig(ssid="Cudy-FA5C", password="58448069"), # From create_cudy
            websocket=WebsocketConfig(server="ws://server.riftoperation.ethan-folio.fr", path="/ws") # From create_prod
        )
