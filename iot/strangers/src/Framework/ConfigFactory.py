from src.Framework.Config import Config, WifiConfig, WebsocketConfig

class ConfigFactory:
    @staticmethod
    def create_ethan_house_config():
        """Create configuration for Ethan's house network"""
        wifi_config = WifiConfig(
            ssid="methilwifi",
            password="DhEubKPM96xd4yp3Pp",
            timeout=15,
            auto_reconnect=True
        )
        
        websocket_config = WebsocketConfig(
            server="ws://YOUR_WEBSOCKET_SERVER_ADDRESS",
            path="/YOUR_WEBSOCKET_PATH",
            reconnect_delay=10,
            ping_interval=60
        )
        
        return Config(
            wifi=wifi_config,
            websocket=websocket_config,
            device_id="ETHAN_HOUSE_ESP32",
            debug_mode=True,
            heartbeat_interval=15
        )
    
    @staticmethod
    def create_default_config():
        """Create default configuration"""
        return Config()
    
    @staticmethod
    def create_custom_config(wifi_ssid, wifi_password, websocket_server, websocket_path, 
                           device_id="CUSTOM_ESP32", debug_mode=False):
        """Create custom configuration"""
        wifi_config = WifiConfig(
            ssid=wifi_ssid,
            password=wifi_password
        )
        
        websocket_config = WebsocketConfig(
            server=websocket_server,
            path=websocket_path
        )
        
        return Config(
            wifi=wifi_config,
            websocket=websocket_config,
            device_id=device_id,
            debug_mode=debug_mode
        )