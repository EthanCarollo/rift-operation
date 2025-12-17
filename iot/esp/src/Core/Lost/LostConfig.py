"""
LostConfig.py - Dedicated configuration for LOST workshop
"""
from src.Framework.Config.Config import WifiConfig, WebsocketConfig
from src.Framework.Config.ConfigFactory import WifiConfigFactory, WebsocketConfigFactory

class LostConfig:
    def __init__(self, role="child"):
        self.role = role

class Config:
    def __init__(self, role="child", wifi=None, websocket=None, device_id="LOST_ESP"):
        self.wifi = wifi if wifi else WifiConfig()
        self.websocket = websocket if websocket else WebsocketConfig()
        self.lost = LostConfig(role=role)
        self.device_id = device_id
        self.debug_mode = True
        self.heartbeat_interval = 15

class LostConfigFactory:
    @staticmethod
    def create_child():
        # Configuration for CHILD
        return Config(
            role="child",
            device_id="LOST-CHILD-ESP",
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod()
        )

    @staticmethod
    def create_parent():
        # Configuration for PARENT
        return Config(
            role="parent",
            device_id="LOST-PARENT-ESP",
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod()
        )
