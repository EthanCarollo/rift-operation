import time
import ujson as json
import uasyncio as asyncio

from src.Framework.EspController import EspController

# --- Constants ---
LONG_PRESS_MS = 1000
WORKSHOP_NAME = "lost"
TARGET_CHILDREN_COUNT = 2
TARGET_PARENT_COUNT   = 2


class LostController(EspController):
    """
    LOST controller for ESP32
    - Listens for the global Rift JSON (children_rift_part_count, parent_rift_part_count, etc.)
    - Starts automatically when counts reach 2/2
    - Sends "status" updates to server (inactive / active)
    - Manages internal steps (distance -> drawing -> light -> cage)
    """

    STEP_IDLE     = 0
    STEP_ACTIVE   = 1
    STEP_DISTANCE = 2
    STEP_DRAWING  = 3
    STEP_LIGHT    = 4
    STEP_CAGE     = 5
    STEP_DONE     = 7

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"

        self.step = self.STEP_IDLE
        self._press_down_ms = None

        self.state = {}
        self.state_initialized = False
        self._session_done_reported = False


    async def send_status(self, status: str):
        """Send current workshop connection status to the server"""
        msg = {
            "type": "workshop_status",
            "value": {
                "workshop": WORKSHOP_NAME,
                "status": status  # "active" or "inactive"
            },
        }
        try:
            await self.websocket_client.send(json.dumps(msg))
            self.logger.info(f"Sent workshop status: {status}")
        except Exception as e:
            self.logger.error(f"Failed to send status '{status}': {e}")

    async def on_websocket_connected(self):
        """Triggered when the WS connection is established"""
        await self.send_status("inactive")

    async def process_message(self, message: str):
        """Handle Rift JSON broadcast or other messages"""
        try:
            data = json.loads(message)
        except Exception:
            self.logger.debug("Ignoring non-JSON message")
            return

        payload = data.get("value") if isinstance(data, dict) and "value" in data else data
        if not isinstance(payload, dict):
            return

        if "children_rift_part_count" not in payload and "parent_rift_part_count" not in payload:
            # Not a Rift JSON
            return

        # Merge relevant values
        self.state.update({k: v for k, v in payload.items() if v is not None})
        self.state_initialized = True
        self.logger.info("Rift JSON state updated")


    async def update(self):
        """
        Called repeatedly by EspController.main()
        - Waits for Rift JSON
        - Starts when counts == 2/2
        - When finished, increments counts and sends them back once
        """
        if not self.state_initialized:
            return

        # Auto-start logic
        if self.step == self.STEP_IDLE:
            c = self.state.get("children_rift_part_count") or 0
            p = self.state.get("parent_rift_part_count") or 0
            if c == TARGET_CHILDREN_COUNT and p == TARGET_PARENT_COUNT:
                await self.start(by="rift_json")
            return
        # End logic
        if self.step == self.STEP_DONE and not self._session_done_reported:
            c = (self.state.get("children_rift_part_count") or 0) + 1
            p = (self.state.get("parent_rift_part_count") or 0) + 1
            self.state["children_rift_part_count"] = c
            self.state["parent_rift_part_count"] = p
            self.state["preset_imagination"] = True
            await self._send_state_to_server()
            await self.send_status("inactive")
            self._session_done_reported = True
            self.logger.info("Workshop finished and counts incremented")

    async def _send_state_to_server(self):
        """Send the current Rift JSON state to the server"""
        try:
            await self.websocket_client.send(json.dumps(self.state))
            self.logger.debug("Sent Rift JSON state")
        except Exception as e:
            self.logger.error(f"Failed to send state: {e}")

    # -------------------------------------------------------------------------
    # Scenario logic
    # -------------------------------------------------------------------------
    async def start(self, by="server_start"):
        if self.step != self.STEP_IDLE:
            self.logger.info(f"Ignoring start, current step={self.step}")
            return

        self.step = self.STEP_ACTIVE
        self._session_done_reported = False
        self.logger.info("Lost workshop started !")
        # Send "active" status
        await self.send_status("active")
        # Start telemetry
        await self.emit("system", "workshop_lost_started", {"by": by})
        await self.emit("parent", "speaker", {"action": "on"})
        await self.emit("child", "animals_led", {"action": "on"})

    async def next_step(self):
        # STEP_ACTIVE -> STEP_DISTANCE
        if self.step == self.STEP_ACTIVE:
            await self.emit("child", "distance_sensor", {"action": "triggered"})
            await self.emit("child", "llm", {"action": "triggered"})
            await self.emit("child", "speaker", {"action": "started"})
            self.step = self.STEP_DISTANCE
            return

        # STEP_DISTANCE -> STEP_DRAWING
        if self.step == self.STEP_DISTANCE:
            await self.emit("child", "drawing", {"action": "read"})
            await self.emit("child", "llm", {"action": "triggered"})
            await self.emit(
                "child", "drawing", {"action": "recognized", "label": "flashlight"}
            )
            self.state["torch_scanned"] = True
            await self._send_state_to_server()
            await self.emit("parent", "lamp", {"action": "on"})
            self.step = self.STEP_DRAWING
            return

        # STEP_DRAWING -> STEP_LIGHT
        if self.step == self.STEP_DRAWING:
            await self.emit("parent", "light_sensor", {"action": "triggered"})
            await self.emit("parent", "mapping_video", {"action": "switch", "to": "reveal"})
            self.step = self.STEP_LIGHT
            return

        # STEP_LIGHT -> STEP_CAGE -> STEP_DONE
        if self.step == self.STEP_LIGHT:
            await self.emit("child", "cage_rfid", {"action": "detected", "tag": "CAGE_A"})
            await self.emit("child", "cage_rfid", {"action": "correct", "tag": "CAGE_A"})
            self.state["cage_is_on_monster"] = True
            await self._send_state_to_server()
            self.step = self.STEP_CAGE
            # Auto-finish
            await self.emit("child", "servo_trap", {"action": "open"})
            await self.emit("parent", "servo_trap", {"action": "open"})
            await self.emit("system", "workshop", {"action": "finished"})
            self.step = self.STEP_DONE
            self.logger.info("Workshop finished")
            return

    async def reset(self, by="server_reset"):
        self.step = self.STEP_IDLE
        self._session_done_reported = False
        self.state.clear()
        self.state_initialized = False
        await self.emit("system", "workshop", {"action": "reset", "by": by})
        await self.send_status("inactive")
        self.logger.info("Lost workshop reset")


    async def emit(self, room: str, event: str, payload: dict):
        msg = {
            "type": "telemetry",
            "value": {
                "deviceId": self.config.device_id,
                "workshop": WORKSHOP_NAME,
                "tsMs": time.ticks_ms(),
                "room": room,
                "event": event,
            },
        }
        msg["value"].update(payload)
        try:
            await self.websocket_client.send(json.dumps(msg))
        except Exception as e:
            self.logger.error(f"Failed to emit telemetry {event}: {e}")
