from .Config import Config, WifiConfig, WebsocketConfig

class WifiConfigFactory:
    @staticmethod
    def create_ethan_house():
        return WifiConfig(
            ssid="Freebox-A01429",
            password="5f4ktqwkwkqdx62rqcdwxs",
            timeout=15,
            auto_reconnect=True
        )
    
    @staticmethod
    def create_antho_house():
        return WifiConfig(
            ssid="Freebox-A01429",
            password="5f4ktqwkwkqdx62rqcdwxs",
            timeout=15,
            auto_reconnect=True
        )

    @staticmethod
    def create_cudy():
        return WifiConfig(
            ssid="Cudy-FA5C",
            password="58448069",
            timeout=15,
            auto_reconnect=True
        )

    @staticmethod
    def create_ethan_mobile():
        return WifiConfig(
            ssid="fourmiphone",
            password="fourmiduterroir74",
            timeout=15,
            auto_reconnect=True
        )

    @staticmethod
    def create_appartment_aix():
        return WifiConfig(
            ssid="SFR_F48F",
            password="7b2uj3mb37js72glj1e9",
            timeout=15,
            auto_reconnect=True
        )

    @staticmethod
    def create_custom(ssid, password):
        return WifiConfig(
            ssid=ssid,
            password=password
        )

class WebsocketConfigFactory:
    @staticmethod
    def create_prod():
        return WebsocketConfig(
            server="ws://192.168.10.7:8000",
            path="/ws",
            reconnect_delay=10,
            ping_interval=60
        )
    
    @staticmethod
    def create_dev():
        return WebsocketConfig(
            server="ws://server.riftoperation.ethan-folio.fr",
            path="/ws",
            reconnect_delay=10,
            ping_interval=60
        )

    @staticmethod
    def create_custom(server, path):
        return WebsocketConfig(
            server=server,
            path=path
        )

class ConfigFactory:
    @staticmethod
    def create_operator_config():
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="OPERATOR-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_table_config():
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id=f"TABLE-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )
    
    @staticmethod
    def create_lost_config(role):
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id=f"LOST-{role.upper()}-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_cudy_depth_config_home():
        return Config(
            wifi=WifiConfigFactory.create_antho_house(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="DEPTH-HOME-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_cudy_rift_config():
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="RIFT-LED-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_cudy_stranger_config():
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="STRANGER-DREAM-SCRABBLE-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )
    @staticmethod
    def create_cudy_stranger_cosmo_config():
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="STRANGER-DREAM-COSMO-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )
    
    @staticmethod
    def create_ethan_house_config():
        return Config(
            wifi=WifiConfigFactory.create_ethan_house(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="ETHAN_HOUSE_ESP32",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_cudy_config():
        return Config(
            wifi=WifiConfigFactory.create_cudy(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="CUDY-FA5C-ESP",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_ethan_mobile_config():
        return Config(
            wifi=WifiConfigFactory.create_ethan_mobile(),
            websocket=WebsocketConfigFactory.create_prod(),
            device_id="FOURMI_PHONE_ESP32",
            debug_mode=True,
            heartbeat_interval=15
        )

    @staticmethod
    def create_default_config():
        return Config()
    
    @staticmethod
    def create_custom_config(wifi_ssid, wifi_password, websocket_server, websocket_path, 
                           device_id="CUSTOM_ESP32", debug_mode=False):
        return Config(
            wifi=WifiConfigFactory.create_custom(wifi_ssid, wifi_password),
            websocket=WebsocketConfigFactory.create_custom(websocket_server, websocket_path),
            device_id=device_id,
            debug_mode=debug_mode
        )