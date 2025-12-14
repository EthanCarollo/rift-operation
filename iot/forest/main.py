import time
import machine

from config import (
    WIFI_SSID, WIFI_PASS, WS_URL,
    PIN_BUTTON, DEBOUNCE_MS,
)

from src.Framework.utils import log, now_ms
from src.Framework.wifi import WifiManager
from src.Framework.wsclient import WsClient
from src.Framework.button import ButtonInput
from src.Core.forest_workshop import ForestWorkshopSimulator


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
        # Server messages (activation / control)
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
