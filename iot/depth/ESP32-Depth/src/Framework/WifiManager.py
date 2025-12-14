import network
import time

class WifiManager:
    def __init__(self, ssid, password, logger=None, timeout=10, auto_reconnect=True):
        self.ssid = ssid
        self.password = password
        self.logger = logger
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self.wlan = network.WLAN(network.STA_IF)
    
    def connect(self):
        if self.logger:
            self.logger.info(f"Connecting to WiFi: {self.ssid}")
        
        self.wlan.active(True)
        
        if self.wlan.isconnected():
            if self.logger:
                self.logger.info("Already connected to WiFi")
            return True
        
        self.wlan.connect(self.ssid, self.password)
        
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > self.timeout:
                if self.logger:
                    self.logger.error("WiFi connection timeout")
                return False
            time.sleep(0.1)
        
        if self.logger:
            self.logger.info(f"WiFi connected: {self.wlan.ifconfig()}")
        return True
    
    def disconnect(self):
        if self.logger:
            self.logger.info("Disconnecting from WiFi")
        self.wlan.active(False)
    
    def is_connected(self):
        return self.wlan.isconnected()
    
    def get_ip(self):
        return self.wlan.ifconfig()[0] if self.wlan.isconnected() else None