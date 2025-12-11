import network
import time

def now_ms():
    return time.ticks_ms()

class WifiManager:
    def __init__(self, ssid, password, logger=None):
        self.ssid = ssid
        self.password = password
        self.logger = logger

        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

    def connect(self, retries=5, timeout_ms=15000):
        if self.logger:
            self.logger.info("Preparing WiFi interfaces")

        self._prepare_interfaces()

        for attempt in range(1, retries + 1):
            if self.logger:
                self.logger.info(f"Connecting to WiFi '{self.ssid}' (attempt {attempt}/{retries})")

            try:
                self.sta.connect(self.ssid, self.password)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"connect() failed: {e}")
                self._reset_sta()
                continue

            t0 = now_ms()
            while not self.sta.isconnected():
                st = self.sta.status()

                # Error states: -3, -2, -1 (per ESP32 MicroPython)
                if st in (-3, -2, -1):
                    if self.logger:
                        self.logger.warning(f"WiFi error status {st}")
                    break

                if time.ticks_diff(now_ms(), t0) > timeout_ms:
                    if self.logger:
                        self.logger.warning("WiFi connect timeout")
                    break

                time.sleep(0.3)

            if self.sta.isconnected():
                cfg = self.sta.ifconfig()
                if self.logger:
                    self.logger.info("WiFi connected")
                    self.logger.debug(f"IP config: {cfg}")
                return True

            # Failed, reset and retry
            if self.logger:
                self.logger.warning("Connection failed, resetting WiFi and retrying...")
            self._reset_sta()

        if self.logger:
            self.logger.error("All WiFi connection attempts failed")

        return False

    def _prepare_interfaces(self):
        # Disable AP mode (prevents unstable WiFi states)
        try:
            if self.ap.active():
                if self.logger:
                    self.logger.debug("Disabling AP mode")
                self.ap.active(False)
                time.sleep(0.2)
        except Exception:
            pass

        self._reset_sta()

    def _reset_sta(self):
        if self.logger:
            self.logger.debug("Resetting STA interface")

        try:
            self.sta.disconnect()
        except Exception:
            pass

        self.sta.active(False)
        time.sleep(0.3)

        self.sta.active(True)
        time.sleep(0.3)
