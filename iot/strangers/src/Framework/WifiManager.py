import network
import uasyncio as asyncio

class WifiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = None

    def connect(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        if not self.wlan.isconnected():
            self.wlan.connect(self.ssid, self.password)
            
            max_wait = 10
            while max_wait > 0:
                if self.wlan.status() < 0 or self.wlan.status() >= 3:
                    break
                max_wait -= 1
                asyncio.sleep(1)
        
        return self.wlan.isconnected()

    def disconnect(self):
        if self.wlan is not None:
            self.wlan.disconnect()
            self.wlan = None