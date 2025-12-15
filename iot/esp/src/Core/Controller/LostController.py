import time
import ujson as json
import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData
from src.Framework.Button.Button import Button
from src.Core.Controller.Lost.LostButtonDelegate import LostButtonDelegate

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
    - Sends "status" updates to server ("inactive" / "active")
    - Sends ONLY 2 Rift JSON updates:
        1) torch_scanned = True
        2) cage_is_on_monster = True + counts incremented + preset_imagination = True
    - Manages internal steps (distance -> drawing -> light -> cage)
    - Exposes handle_short_press() which is called by LostButtonDelegate
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

        self.state_initialized = False
        self.children_rift_part_count = None
        self.parent_rift_part_count = None
        # Internal flags to avoid resending same JSON multiple times
        self.torch_scanned_sent = False
        self.cage_sent = False
        self._session_done_reported = False
        # Hardware button (GPIO 27)
        self.button = Button(pin_id=27, delegate=LostButtonDelegate(self))

    async def send_status(self, status: str):
        """
        Send current workshop connection status to the server.
        status: "active" | "inactive"
        """
        msg = {
            "type": "workshop_status",
            "value": {
                "workshop": WORKSHOP_NAME,
                "status": status,
            },
        }
        try:
            await self.websocket_client.send(json.dumps(msg))
            self.logger.info("Sent workshop status: {}".format(status))
        except Exception as e:
            self.logger.error("Failed to send status '{}': {}".format(status, e))

    async def send_rift_json(self, **kwargs):
        """
        Build and send a RiftOperationJsonData payload with only the provided fields
        """
        data = RiftOperationJsonData(**kwargs)
        try:
            payload = data.to_json()
            await self.websocket_client.send(payload)
            self.logger.info("Sent Rift JSON: {}".format(payload))
        except Exception as e:
            self.logger.error("Failed to send Rift JSON: {}".format(e))

    async def on_websocket_connected(self):
        """
        Hook called by EspController right after WebSocket connection.
        Initial status is always "inactive"
        """
        await self.send_status("inactive")

    async def process_message(self, message: str):
        """
        Handle Rift JSON broadcast or other messages coming from the server.
        We only care about children_rift_part_count / parent_rift_part_count
        """
        try:
            data = json.loads(message)
        except Exception:
            self.logger.debug("Ignoring non-JSON message")
            return

        payload = data.get("value") if isinstance(data, dict) and "value" in data else data
        if not isinstance(payload, dict):
            return

        # If both keys are missing, this is not the Rift JSON we care about
        if "children_rift_part_count" not in payload and "parent_rift_part_count" not in payload:
            return
        # Update local counters (if present)
        if "children_rift_part_count" in payload and payload["children_rift_part_count"] is not None:
            self.children_rift_part_count = payload["children_rift_part_count"]
        if "parent_rift_part_count" in payload and payload["parent_rift_part_count"] is not None:
            self.parent_rift_part_count = payload["parent_rift_part_count"]

        self.state_initialized = True
        self.logger.info(
            "Rift JSON state updated: children={}, parent={}".format(
                self.children_rift_part_count, self.parent_rift_part_count
            )
        )

    # -------------------------------------------------------------------------
    # Main update loop (called by EspController.main)
    # -------------------------------------------------------------------------

    async def update(self):
        """
        Called repeatedly by EspController.main()

        - Waits for first Rift JSON (state_initialized == True)
        - When in IDLE and counts == 2/2 -> auto-start
        - When DONE and not yet reported -> increments counts and sends final Rift JSON
        """
        if not self.state_initialized:
            return

        # Auto-start logic
        if self.step == self.STEP_IDLE:
            c = self.children_rift_part_count or 0
            p = self.parent_rift_part_count or 0

            if c == TARGET_CHILDREN_COUNT and p == TARGET_PARENT_COUNT:
                await self.start(by="rift_json")
            return
        # End of workshop logic
        if self.step == self.STEP_DONE and not self._session_done_reported:
            c = (self.children_rift_part_count or 0) + 1
            p = (self.parent_rift_part_count or 0) + 1
            self.children_rift_part_count = c
            self.parent_rift_part_count = p

            # Send final Rift JSON:
            # - updated counts
            # - cage_is_on_monster already True
            # - preset_imagination = True
            await self.send_rift_json(
                children_rift_part_count=c,
                parent_rift_part_count=p,
                torch_scanned=True,
                cage_is_on_monster=True,
                preset_imagination=True,
            )
            # Status back to inactive
            await self.send_status("inactive")

            self._session_done_reported = True
            self.logger.info(
                "Workshop finished and counts incremented: children={}, parent={}".format(
                    c, p
                )
            )

    async def start(self, by="server_start"):
        if self.step != self.STEP_IDLE:
            self.logger.info("Ignoring start, current step={}".format(self.step))
            return

        self.step = self.STEP_ACTIVE
        self._session_done_reported = False
        self.torch_scanned_sent = False
        self.cage_sent = False

        self.logger.info("Lost workshop started")

        # Status → active
        await self.send_status("active")
        self._log_telemetry("system", "workshop_lost_started", {"by": by})
        self._log_telemetry("parent", "speaker", {"action": "on"})
        self._log_telemetry("child", "animals_led", {"action": "on"})

    async def handle_short_press(self):
        """
        Called by LostButtonDelegate when the hardware button is pressed shortly
        """
        if self.step == self.STEP_DONE:
            self.logger.debug("Short press ignored: already DONE")
            return

        self.logger.info("BTN action: next_step")
        await self.next_step()

    async def next_step(self):
        # STEP_ACTIVE -> STEP_DISTANCE
        if self.step == self.STEP_ACTIVE:
            self._log_telemetry("child", "distance_sensor", {"action": "triggered"})
            self._log_telemetry("child", "llm", {"action": "triggered"})
            self._log_telemetry("child", "speaker", {"action": "started"})
            self.step = self.STEP_DISTANCE
            return

        # STEP_DISTANCE -> STEP_DRAWING
        if self.step == self.STEP_DISTANCE:
            self._log_telemetry("child", "drawing", {"action": "read"})
            self._log_telemetry("child", "llm", {"action": "triggered"})
            self._log_telemetry(
                "child",
                "drawing",
                {"action": "recognized", "label": "flashlight"},
            )
            # --- RIFT JSON #1: torch_scanned = True ---
            if not self.torch_scanned_sent:
                await self.send_rift_json(torch_scanned=True)
                self.torch_scanned_sent = True

            self._log_telemetry("parent", "lamp", {"action": "on"})
            self.step = self.STEP_DRAWING
            return

        # STEP_DRAWING -> STEP_LIGHT
        if self.step == self.STEP_DRAWING:
            self._log_telemetry("parent", "light_sensor", {"action": "triggered"})
            self._log_telemetry(
                "parent",
                "mapping_video",
                {"action": "switch", "to": "reveal"},
            )
            self.step = self.STEP_LIGHT
            return

        # STEP_LIGHT -> STEP_CAGE -> STEP_DONE
        if self.step == self.STEP_LIGHT:
            self._log_telemetry(
                "child",
                "cage_rfid",
                {"action": "detected", "tag": "CAGE_A"},
            )
            self._log_telemetry(
                "child",
                "cage_rfid",
                {"action": "correct", "tag": "CAGE_A"},
            )
            self.step = self.STEP_CAGE
            # Auto-finish
            self._log_telemetry("child", "servo_trap", {"action": "open"})
            self._log_telemetry("parent", "servo_trap", {"action": "open"})
            self._log_telemetry("system", "workshop", {"action": "finished"})
            self.step = self.STEP_DONE
            self.logger.info("Workshop finished (waiting for final Rift JSON send)")
            return

    async def reset(self, by="server_reset"):
        """
        Reset internal state and notify server
        """
        self.step = self.STEP_IDLE
        self._session_done_reported = False
        self.state_initialized = False
        self.children_rift_part_count = None
        self.parent_rift_part_count = None
        self.torch_scanned_sent = False
        self.cage_sent = False

        await self.send_status("inactive")
        self.logger.info("Lost workshop reset")

    # -------------------------------------------------------------------------
    # Telemetry helper
    # -------------------------------------------------------------------------
    def _log_telemetry(self, room: str, event: str, payload: dict):
        """
        Internal helper to log what used to be WebSocket telemetry.
        This does NOT send anything over the network
        """
        self.logger.debug(
            "[TELEMETRY] room={} event={} payload={}".format(room, event, payload)
        )