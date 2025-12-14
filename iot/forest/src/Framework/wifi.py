import time
import network
from .utils import log, now_ms


class WifiManager:
    # Connect ESP32 to Wi-Fi (STA mode)
    def __init__(self, ssid: str, password: str):
        self.ssid = ssid
        self.password = password
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

    def connect(self, retries: int = 5, timeout_ms: int = 15000) -> bool:
        self._prepare_interfaces()

        for _ in range(retries):
            try:
                self.sta.connect(self.ssid, self.password)
            except Exception:
                self._reset_sta()
                continue

            t0 = now_ms()
            while not self.sta.isconnected():
                st = self.sta.status()
                # -2 no AP / -3 wrong pass / -1 fail / 1 connecting / 3 got ip
                if st in (-3, -2, -1):
                    break
                if time.ticks_diff(now_ms(), t0) > timeout_ms:
                    break
                time.sleep(0.3)

            if self.sta.isconnected():
                log("WiFi OK:", self.sta.ifconfig())
                return True

            self._reset_sta()

        return False

    def _prepare_interfaces(self) -> None:
        # Disable AP mode to avoid unstable Wi-Fi states
        try:
            if self.ap.active():
                self.ap.active(False)
                time.sleep(0.2)
        except Exception:
            pass
        self._reset_sta()

    def _reset_sta(self) -> None:
        try:
            self.sta.disconnect()
        except Exception:
            pass
        self.sta.active(False)
        time.sleep(0.3)
        self.sta.active(True)
        time.sleep(0.3)
