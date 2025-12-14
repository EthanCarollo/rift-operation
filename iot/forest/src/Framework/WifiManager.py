import network
import time

def now_ms():
    return time.ticks_ms()

class WifiManager:
    # Connect ESP32 to Wi-Fi (STA mode)
    def __init__(self, wifi_config, logger):
        self.cfg = wifi_config
        self.log = logger

        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

    def connect(self, retries=5, timeout_ms=15000):
        self._prepare_interfaces()

        for attempt in range(1, retries + 1):
            self.log.info("WiFi connect attempt", attempt, "/", retries, "->", self.cfg.ssid)
            try:
                self.sta.connect(self.cfg.ssid, self.cfg.password)
            except Exception as e:
                self.log.error("WiFi connect() error:", repr(e))
                self._reset_sta()
                continue

            t0 = now_ms()
            while not self.sta.isconnected():
                st = self.sta.status()
                # -2 no AP / -3 wrong pass / -1 fail / 1 connecting / 3 got ip
                if st in (-3, -2, -1):
                    self.log.error("WiFi status error:", st)
                    break
                if time.ticks_diff(now_ms(), t0) > timeout_ms:
                    self.log.error("WiFi timeout")
                    break
                time.sleep(0.3)

            if self.sta.isconnected():
                self.log.info("WiFi OK:", self.sta.ifconfig())
                return True

            self.log.info("WiFi retry...")
            self._reset_sta()

        self.log.error("WiFi FAILED after", retries, "attempts")
        return False

    def _prepare_interfaces(self):
        # Disable AP mode to avoid unstable Wi-Fi states
        try:
            if self.ap.active():
                self.log.debug("Disable AP mode")
                self.ap.active(False)
                time.sleep(0.2)
        except Exception:
            pass
        self._reset_sta()

    def _reset_sta(self):
        try:
            self.sta.disconnect()
        except Exception:
            pass
        self.sta.active(False)
        time.sleep(0.3)
        self.sta.active(True)
        time.sleep(0.3)
