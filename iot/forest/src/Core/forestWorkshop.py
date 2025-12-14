import time
import ujson
from config import (
    DOUBLE_PRESS_MS,
    LONG_PRESS_MS,
)


class ForestWorkshopSimulator:
    # Steps are intentionally explicit and linear for demo purposes.
    STEP_IDLE = 0
    STEP_ACTIVE = 1
    STEP_DISTANCE = 2
    STEP_DRAWING = 3
    STEP_LIGHT = 4
    STEP_CAGE = 5
    STEP_KEYS = 6
    STEP_DONE = 7

    def __init__(self, ws_client, device_config, logger):
        self.ws = ws_client
        self.device = device_config
        self.log = logger

        self.step = self.STEP_IDLE

        self._last_press_ms = 0
        self._press_down_ms = None

    def on_server_message(self, raw_text):
        """Handle server messages and start the forest flow when requested."""
        try:
            msg = ujson.loads(raw_text)
        except Exception:
            return

        t = msg.get("type")
        v = msg.get("value")

        # Expected: {"type":"workshop", "value":{"name":"forest","action":"start"}}
        if t == "workshop" and isinstance(v, dict):
            if v.get("name") == self.device.workshop and v.get("action") == "start":
                self.start()

    def start(self):
        if self.step != self.STEP_IDLE:
            return
        self.step = self.STEP_ACTIVE

        self.log.info("Forest workshop started")

        # System event: start
        self.emit("system", "workshop_forest_started", {"by": "server_start"})

        # Parent: start audio
        self.emit("parent", "speaker", {"action": "on"})
        # Child: start animal LEDs
        self.emit("child", "animals_led", {"action": "on"})

    def handle_button(self, pressed, now_ms):
        if pressed:
            self.log.debug("BTN pressed @", now_ms, "step=", self.step)
            self._press_down_ms = now_ms
            return

        if self._press_down_ms is None:
            return

        duration = time.ticks_diff(now_ms, self._press_down_ms)
        self._press_down_ms = None

        self.log.debug("BTN duration=", duration, "ms")

        # Long press = incorrect cage only during RFID step
        if duration >= LONG_PRESS_MS and self.step == self.STEP_CAGE:
            self.log.info("BTN action: cage_incorrect (long press)")
            self.cage_incorrect()
            return

        # Ignore long press outside the RFID step
        if duration >= LONG_PRESS_MS:
            self.log.debug("BTN action: ignored (long press outside cage step)")
            return

        if self.step == self.STEP_DONE:
            return

        self.log.info("BTN action: next_step")
        self.next_step()

    def next_step(self):
        if self.step == self.STEP_ACTIVE:
            # Simulate distance sensor triggered + LLM speaker started
            self.emit("child", "distance_sensor", {"action": "triggered"})
            self.emit("child", "llm", {"action": "triggered"})
            self.emit("child", "speaker", {"action": "started"})
            self.step = self.STEP_DISTANCE
            return

        if self.step == self.STEP_DISTANCE:
            # Simulate drawing flow + parent lamp on
            self.emit("child", "drawing", {"action": "read"})
            self.emit("child", "llm", {"action": "triggered"})
            self.emit("child", "drawing", {"action": "recognized", "label": "flashlight"})
            self.emit("parent", "lamp", {"action": "on"})
            self.step = self.STEP_DRAWING
            return

        if self.step == self.STEP_DRAWING:
            # Simulate light sensor + video switch
            self.emit("parent", "light_sensor", {"action": "triggered"})
            self.emit("parent", "mapping_video", {"action": "switch", "to": "reveal"})
            self.step = self.STEP_LIGHT
            return

        if self.step == self.STEP_LIGHT:
            # Simulate cage RFID detected + correct cage
            self.emit("child", "cage_rfid", {"action": "detected", "tag": "CAGE_A"})
            self.emit("child", "cage_rfid", {"action": "correct", "tag": "CAGE_A"})
            self.step = self.STEP_CAGE

            # Auto-finish after correct cage: traps + finished
            self.emit("child", "servo_trap", {"action": "open"})
            self.emit("parent", "servo_trap", {"action": "open"})
            self.emit("system", "workshop", {"action": "finished"})
            self.step = self.STEP_DONE
            self.log.info("Forest workshop finished")
            return

    def cage_incorrect(self):
        # Simulate wrong cage + animals feedback + LLM speaker feedback
        self.emit("child", "cage_rfid", {"action": "incorrect", "tag": "CAGE_X"})
        self.emit("child", "animals_speaker", {"action": "on", "reason": "wrong_cage"})
        self.log.info("Cage incorrect simulated")

    def reset(self):
        self.step = self.STEP_IDLE
        self.emit("system", "workshop", {"action": "reset"})
        self.log.info("Simulation reset")

    def emit(self, room, event, payload):
        msg = {
            "type": "telemetry",
            "value": {
                "deviceId": self.device.device_id,
                "workshop": self.device.workshop,
                "tsMs": time.ticks_ms(),
                "room": room,  # "parent" | "child" | "system"
                "event": event,
            }
        }
        msg["value"].update(payload)
        self.ws.send_json(msg)
