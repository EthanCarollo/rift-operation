"""
DepthConfig.py - Dedicated configuration for DEPTH workshop
"""
from src.Framework.Config.Config import WifiConfig, WebsocketConfig

class DepthConfig:
    def __init__(self, role="child", button_pins=None, led_pins=None, partitions=None):
        self.role = role
        self.button_pins = button_pins or {1: 14, 2: 19, 3: 23}
        self.led_pins = led_pins or {1: 25, 2: 32, 3: 33}
        # Bleu : 1, Rouge : 2, Vert : 3
        self.partitions = partitions or {
            1: [1, 2, 1, 3, 1, 2, 1, 3],
            2: [1, 1, 3, 3, 2, 3, 2, 1, 1, 3, 3, 2, 3],
            3: [1, 1, 1, 2, 3, 2, 1, 3, 2, 2, 1, 1, 1, 1, 2, 3, 2, 1, 3, 2, 2, 1]
        }

class Config:
    def __init__(self, role="child"):
        self.depth = DepthConfig(role=role)

class DepthConfigFactory:
    @staticmethod
    def create_default_child():
        return Config(
            role="nightmare"
        )
