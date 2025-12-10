import time
import ujson
import network
import machine
from machine import Pin

from config import (
    DEBUG,
    WIFI_SSID, WIFI_PASS, WS_URL,
    PIN_BUTTON, DEBOUNCE_MS,
    DEVICE_ID, WORKSHOP,
    SEND_HELLO_ON_CONNECT,
)

from lib.websocketclient import connect
from workshop import ForestWorkshopSimulator


def log(*args):
    if DEBUG:
        print("[IOT]", *args)


def now_ms():
    return time.ticks_ms()


class WifiManager:
    # Connect ESP32 to Wi-Fi (STA mode)
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

    def connect(self, retries=5, timeout_ms=15000):
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

    def _prepare_interfaces(self):
        # Disable AP mode to avoid unstable Wi-Fi states
        try:
            if self.ap.active():
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


class WsClient:
    # Minimal WebSocket client (auto reconnect, JSON send, non-blocking recv)
    def __init__(self, url):
        self.url = url
        self.socket = None

    def ensure_connected(self):
        if self.socket:
            return True

        try:
            log("WS connecting:", self.url)
            self.socket = connect(self.url, timeout=8)
            log("WS connected")

            if SEND_HELLO_ON_CONNECT:
                self.send_json({
                    "type": "hello",
                    "value": {"deviceId": DEVICE_ID, "workshop": WORKSHOP}
                })

            return True
        except Exception as e:
            log("WS connect error:", repr(e))
            self.socket = None
            return False

    def send_json(self, obj):
        try:
            if not self.ensure_connected():
                return False
            msg = ujson.dumps(obj)
            self.socket.send(msg)
            log("WS >>", msg)
            return True
        except Exception as e:
            log("WS send error:", repr(e))
            self.close(reason="send_error")
            return False

    def poll_recv(self):
        """Return a raw text message if available"""
        if not self.socket:
            return None
        try:
            if self.socket.poll(0):
                return self.socket.recv()
        except Exception as e:
            log("WS recv error:", repr(e))
            self.close(reason="recv_error")
        return None

    def close(self, reason="client_close"):
        if self.socket:
            try:
                msg = {
                    "type": "disconnect",
                    "value": {
                        "deviceId": DEVICE_ID,
                        "workshop": WORKSHOP,
                        "reason": reason,
                        "tsMs": now_ms(),
                    }
                }
                self.socket.send(ujson.dumps(msg))
            except Exception:
                pass

            try:
                self.socket.close()
            except Exception:
                pass

        self.socket = None
        log("WS closed")


class ButtonInput:
    # Debounced button with press/release events
    def __init__(self, pin, debounce_ms):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms

        self._last_value = self.button.value()
        self._last_change_ms = 0

    def update(self, now):
        """
        Returns:
          - True for pressed
          - False for released
          - None for no change
        """
        current = self.button.value()
        if current == self._last_value:
            return None

        if time.ticks_diff(now, self._last_change_ms) <= self.debounce_ms:
            return None

        self._last_change_ms = now
        self._last_value = current
        return (current == 0)


def main():
    log("Booting...")

    wifi = WifiManager(WIFI_SSID, WIFI_PASS)
    if not wifi.connect():
        log("WiFi FAILED")
        time.sleep(2)
        machine.reset()

    ws = WsClient(WS_URL)
    ws.ensure_connected()

    simulator = ForestWorkshopSimulator(ws, log)
    button = ButtonInput(PIN_BUTTON, DEBOUNCE_MS)

    log("Ready. Waiting for server activation or manual start")

    while True:
        # Server messages (activation)
        raw = ws.poll_recv()
        if raw:
            simulator.on_server_message(raw)
        # Button events (press/release)
        now = now_ms()
        evt = button.update(now)
        if evt is not None:
            simulator.handle_button(pressed=evt, now_ms=now)

        time.sleep(0.02)


try:
    main()
except Exception as e:
    log("Fatal:", repr(e))
    time.sleep(1)
    machine.reset()
