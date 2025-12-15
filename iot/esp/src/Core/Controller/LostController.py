import time
import ujson as json
import uasyncio as asyncio

from src.Framework.EspController import EspController

# === Constantes ===
LONG_PRESS_MS = 1000
ACTIVATE_TYPE = "workshop"
WORKSHOP_NAME = "lost"


class LostController(EspController):
    # Steps are intentionally explicit and linear for demo purposes
    STEP_IDLE = 0
    STEP_ACTIVE = 1
    STEP_DISTANCE = 2
    STEP_DRAWING = 3
    STEP_LIGHT = 4
    STEP_CAGE = 5
    STEP_KEYS = 6
    STEP_DONE = 7

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"

        self.step = self.STEP_IDLE
        self._press_down_ms = None

    async def process_message(self, message: str):
        """Handle server messages and start the forest flow when requested."""
        try:
            data = json.loads(message)
        except Exception:
            self.logger.debug(f"Ignoring non-JSON message: {message}")
            return

        msg_type = data.get("type")
        value = data.get("value")

        if msg_type != ACTIVATE_TYPE:
            return

        if not isinstance(value, dict):
            return

        name = value.get("name")
        action = value.get("action")

        if name not in (WORKSHOP_NAME,):
            return

        if action == "start":
            await self.start(by="server_start")
        elif action == "reset":
            await self.reset(by="server_reset")

    async def start(self, by: str = "server_start"):
        if self.step != self.STEP_IDLE:
            self.logger.info(f"Ignoring start, current step={self.step}")
            return

        self.step = self.STEP_ACTIVE
        self.logger.info("Lost / Forest workshop started")

        await self.emit("system", "workshop_lost_started", {"by": by})
        # Parent: start audio
        await self.emit("parent", "speaker", {"action": "on"})
        # Child: animal LEDs ON
        await self.emit("child", "animals_led", {"action": "on"})

    async def handle_short_press(self):
        if self.step == self.STEP_DONE:
            self.logger.debug("Short press ignored: already DONE")
            return

        self.logger.info("BTN action: next_step")
        await self.next_step()

    async def handle_long_press(self):
        if self.step == self.STEP_CAGE:
            self.logger.info("BTN action: cage_incorrect (long press)")
            await self.cage_incorrect()
        else:
            self.logger.debug("Long press ignored (outside cage step)")

    async def next_step(self):
        # STEP_ACTIVE -> STEP_DISTANCE
        if self.step == self.STEP_ACTIVE:
            # Simulate distance sensor triggered + LLM speaker started
            await self.emit("child", "distance_sensor", {"action": "triggered"})
            await self.emit("child", "llm", {"action": "triggered"})
            await self.emit("child", "speaker", {"action": "started"})
            self.step = self.STEP_DISTANCE
            return

        # STEP_DISTANCE -> STEP_DRAWING
        if self.step == self.STEP_DISTANCE:
            # Simulate drawing flow + parent lamp on
            await self.emit("child", "drawing", {"action": "read"})
            await self.emit("child", "llm", {"action": "triggered"})
            await self.emit(
                "child",
                "drawing",
                {"action": "recognized", "label": "flashlight"},
            )
            await self.emit("parent", "lamp", {"action": "on"})
            self.step = self.STEP_DRAWING
            return

        # STEP_DRAWING -> STEP_LIGHT
        if self.step == self.STEP_DRAWING:
            # Simulate light sensor + mapping video switch
            await self.emit("parent", "light_sensor", {"action": "triggered"})
            await self.emit(
                "parent",
                "mapping_video",
                {"action": "switch", "to": "reveal"},
            )
            self.step = self.STEP_LIGHT
            return

        # STEP_LIGHT -> STEP_CAGE -> STEP_DONE
        if self.step == self.STEP_LIGHT:
            # Simulate cage RFID detected + correct cage
            await self.emit(
                "child",
                "cage_rfid",
                {"action": "detected", "tag": "CAGE_A"},
            )
            await self.emit(
                "child",
                "cage_rfid",
                {"action": "correct", "tag": "CAGE_A"},
            )
            self.step = self.STEP_CAGE
            # Auto-finish after correct cage: traps + finished
            await self.emit("child", "servo_trap", {"action": "open"})
            await self.emit("parent", "servo_trap", {"action": "open"})
            await self.emit("system", "workshop", {"action": "finished"})
            self.step = self.STEP_DONE
            self.logger.info("Lost / Forest workshop finished")
            return

        # STEP_KEYS does not have next step

    async def cage_incorrect(self):
        # Simulate wrong cage + animals feedback + LLM speaker feedback
        await self.emit(
            "child",
            "cage_rfid",
            {"action": "incorrect", "tag": "CAGE_X"},
        )
        await self.emit(
            "child",
            "animals_speaker",
            {"action": "on", "reason": "wrong_cage"},
        )
        self.logger.info("Cage incorrect simulated")

    async def reset(self, by: str = "server_reset"):
        self.step = self.STEP_IDLE
        await self.emit("system", "workshop", {"action": "reset", "by": by})
        self.logger.info("Simulation reset")

    # Send telemetry to server
    async def emit(self, room: str, event: str, payload: dict):
        msg = {
            "type": "telemetry",
            "value": {
                "deviceId": self.config.device_id,
                "workshop": WORKSHOP_NAME,
                "tsMs": time.ticks_ms(),
                "room": room,   # "parent" | "child" | "system"
                "event": event,
            },
        }
        msg["value"].update(payload)

        try:
            await self.websocket_client.send(json.dumps(msg))
        except Exception as e:
            self.logger.error(f"Failed to emit telemetry {event}: {e}")
