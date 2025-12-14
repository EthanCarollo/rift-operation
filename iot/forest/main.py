import time
import machine

from config import (
    DEBUG,
    WIFI_CONFIG,
    WS_CONFIG,
    DEVICE_CONFIG,
    PIN_BUTTON,
    DEBOUNCE_MS,
    SEND_HELLO_ON_CONNECT,
    HEARTBEAT_MS,
)

from src.Framework.Logger import Logger
from src.Framework.WifiManager import WifiManager
from src.Framework.WebSocketClient import WebSocketClient
from src.Framework.Button.ButtonManager import ButtonInput
from src.Core.ForestWorkshop import ForestWorkshopSimulator


def now_ms():
    return time.ticks_ms()


logger = Logger(
    name="IOT",
    level=Logger.LEVEL_DEBUG if DEBUG else Logger.LEVEL_INFO,
)


def main():
    logger.info("Booting...")

    wifi = WifiManager(WIFI_CONFIG, logger)
    if not wifi.connect():
        logger.error("WiFi FAILED, resetting...")
        time.sleep(2)
        machine.reset()

    ws = WebSocketClient(WS_CONFIG, DEVICE_CONFIG, SEND_HELLO_ON_CONNECT, logger)
    ws.ensure_connected()

    simulator = ForestWorkshopSimulator(ws, DEVICE_CONFIG, logger)
    button = ButtonInput(PIN_BUTTON, DEBOUNCE_MS)

    logger.info("Ready. Waiting for server activation or manual start")

    last_heartbeat = now_ms()

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

        # Optional heartbeat
        if HEARTBEAT_MS > 0:
            if time.ticks_diff(now, last_heartbeat) >= HEARTBEAT_MS:
                last_heartbeat = now
                ws.send_json({
                    "type": "telemetry",
                    "value": {
                        "deviceId": DEVICE_CONFIG.device_id,
                        "workshop": DEVICE_CONFIG.workshop,
                        "tsMs": now,
                        "event": "heartbeat",
                    }
                })

        time.sleep(0.02)


try:
    main()
except Exception as e:
    logger.error("Fatal:", repr(e))
    time.sleep(1)
    machine.reset()