from src.Framework.Config import Config, WifiConfig, WebsocketConfig, DepthConfig

class ConfigFactory:
    @staticmethod
    def create_depth_config():
        """Create configuration for Depth experience"""
        wifi_config = WifiConfig(
            ssid="Freebox-A01429",
            password="5f4ktqwkwkqdx62rqcdwxs",
            timeout=15,
            auto_reconnect=True
        )
        
        websocket_config = WebsocketConfig(
            server="ws://192.168.1.133:8080",
            path="/",
            reconnect_delay=10,
            ping_interval=60
        )
        
        depth_config = DepthConfig(
            role="child",  # Can be overridden
            button_pins={1: 14, 2: 19, 3: 23},
            led_pins={1: 25, 2: 32, 3: 33},
            partitions={
                1: [1, 2, 1, 3],
                2: [3, 3, 1],
                3: [2, 1, 2, 3]
            }
        )
        
        return Config(
            wifi=wifi_config,
            websocket=websocket_config,
            depth=depth_config,
            device_id="DEPTH_ESP32",
            debug_mode=True,
            heartbeat_interval=15
        )
    
    @staticmethod
    def create_default_config():
        """Create default configuration"""
        return Config()
    
    @staticmethod
    def create_custom_config(wifi_ssid, wifi_password, websocket_server, websocket_path, 
                           role="child", device_id="CUSTOM_DEPTH_ESP32", debug_mode=False):
        """Create custom configuration"""
        wifi_config = WifiConfig(
            ssid=wifi_ssid,
            password=wifi_password
        )
        
        websocket_config = WebsocketConfig(
            server=websocket_server,
            path=websocket_path
        )
        
        depth_config = DepthConfig(role=role)
        
        return Config(
            wifi=wifi_config,
            websocket=websocket_config,
            depth=depth_config,
            device_id=device_id,
            debug_mode=debug_mode
        )