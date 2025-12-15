import ujson as json
import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Framework.Button.Button import Button
from src.Core.Lost.LostButtonDelegate import LostButtonDelegate


class LostController(EspController):
    """
    LOST controller for ESP32

    - Listens for the global Rift JSON to auto-start when counts reach 2/2
    - Sends Rift JSON updates with: torch_scanned, cage_is_on_monster, preset_lost
    - Manages internal steps (distance -> drawing -> light -> cage)
    """

    # --- Step constants ---
    STEP_IDLE     = 0
    STEP_ACTIVE   = 1
    STEP_DISTANCE = 2
    STEP_DRAWING  = 3
    STEP_LIGHT    = 4
    STEP_CAGE     = 5
    STEP_DONE     = 7
    # --- Target counts to auto-start ---
    TARGET_CHILDREN_COUNT = 2
    TARGET_PARENT_COUNT   = 2

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"

        self.step = self.STEP_IDLE
        self.state_initialized = False
        self.torch_scanned_sent = False
        self._session_done_reported = False
        # Track counts only for auto-start detection
        self._last_children_count = 0
        self._last_parent_count = 0
        # Store the last received payload to modify and resend
        self._last_payload = None
        # Hardware button (GPIO 27)
        self.button = Button(pin_id=27, delegate=LostButtonDelegate(self))

    async def send_rift_json(self, torch_scanned=None, cage_is_on_monster=None, preset_lost=None):
        """
        Modify the last received payload with the specified values and send it back.
        Only modifies torch_scanned, cage_is_on_monster, preset_lost.
        """
        if self._last_payload is None:
            self.logger.error("Cannot send Rift JSON: no payload received yet")
            return

        # Copy the last payload and modify only what we need
        payload_to_send = dict(self._last_payload)
        
        # Change device_id to our own
        payload_to_send["device_id"] = self.config.device_id
        
        # Only update fields that are explicitly set (not None)
        if torch_scanned is not None:
            payload_to_send["torch_scanned"] = torch_scanned
        if cage_is_on_monster is not None:
            payload_to_send["cage_is_on_monster"] = cage_is_on_monster
        if preset_lost is not None:
            payload_to_send["preset_lost"] = preset_lost

        try:
            await self.websocket_client.send(json.dumps(payload_to_send))
            self.logger.info("Sent Rift JSON: torch_scanned={}, cage_is_on_monster={}, preset_lost={}".format(
                payload_to_send.get("torch_scanned"),
                payload_to_send.get("cage_is_on_monster"),
                payload_to_send.get("preset_lost")
            ))
        except Exception as e:
            self.logger.error("Failed to send Rift JSON: {}".format(e))

    async def process_message(self, message: str):
        """
        Handle Rift JSON broadcast from the server.
        Stores the payload for later modification and resending.
        """
        try:
            data = json.loads(message)
        except Exception:
            self.logger.debug("Ignoring non-JSON message")
            return

        payload = data.get("value") if isinstance(data, dict) and "value" in data else data
        if not isinstance(payload, dict):
            return

        # Check if this is the Rift JSON we care about
        if "children_rift_part_count" not in payload and "parent_rift_part_count" not in payload:
            return
        
        # Store the full payload for later modification
        self._last_payload = payload
        
        # Update local counters for auto-start detection only
        if "children_rift_part_count" in payload and payload["children_rift_part_count"] is not None:
            self._last_children_count = payload["children_rift_part_count"]
        if "parent_rift_part_count" in payload and payload["parent_rift_part_count"] is not None:
            self._last_parent_count = payload["parent_rift_part_count"]

        self.state_initialized = True
        self.logger.info("Rift JSON received: children={}, parent={}".format(
            self._last_children_count, self._last_parent_count
        ))

    async def update(self):
        """
        Called repeatedly by EspController.main()
        - Waits for first Rift JSON
        - When in IDLE and counts == 2/2 -> auto-start
        - When DONE and not yet reported -> sends final Rift JSON
        """
        if not self.state_initialized:
            return

        # Auto-start logic
        if self.step == self.STEP_IDLE:
            if (self._last_children_count == self.TARGET_CHILDREN_COUNT and 
                self._last_parent_count == self.TARGET_PARENT_COUNT):
                await self.start(by="rift_json")
            return
        # When workshop is done, send final state
        if self.step == self.STEP_DONE and not self._session_done_reported:
            await self.send_rift_json(
                torch_scanned=True,
                cage_is_on_monster=True,
                preset_lost=False
            )
            self._session_done_reported = True
            self.logger.info("Workshop finished, final Rift JSON sent")

    async def start(self, by="server_start"):
        """
        Start Lost workshop scenario
        """
        if self.step != self.STEP_IDLE:
            self.logger.info("Ignoring start, current step={}".format(self.step))
            return

        self.step = self.STEP_ACTIVE
        self._session_done_reported = False
        self.torch_scanned_sent = False

        self.logger.info("Lost workshop started")
        await self.send_rift_json(preset_lost=True)
        # Log initial telemetry events
        await asyncio.sleep_ms(150)
        self._log_telemetry("system", "workshop_lost_started", {"by": by})
        await asyncio.sleep_ms(150)
        self._log_telemetry("parent", "speaker", {"action": "on"})
        await asyncio.sleep_ms(150)
        self._log_telemetry("child", "animals_led", {"action": "on"})

    async def handle_short_press(self):
        """
        Called by LostButtonDelegate when the hardware button is pressed shortly
        """
        if self.step == self.STEP_DONE:
            self.logger.debug("Short press ignored: already DONE")
            return

        self.logger.info("BTN action: next_step")
        await asyncio.sleep_ms(100)
        await self.next_step()

    async def next_step(self):
        """
        Progress through workshop steps
        """
        # STEP_ACTIVE -> STEP_DISTANCE
        if self.step == self.STEP_ACTIVE:
            self._log_telemetry("child", "distance_sensor", {"action": "triggered"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("child", "llm", {"action": "triggered"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("child", "speaker", {"action": "started"})
            self.step = self.STEP_DISTANCE
            return
        # STEP_DISTANCE -> STEP_DRAWING
        if self.step == self.STEP_DISTANCE:
            self._log_telemetry("child", "drawing", {"action": "read"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("child", "llm", {"action": "triggered"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("child", "drawing", {"action": "recognized", "label": "flashlight"})
            # Send torch_scanned=True when drawing is recognized
            if not self.torch_scanned_sent:
                await asyncio.sleep_ms(150)
                await self.send_rift_json(torch_scanned=True)
                self.torch_scanned_sent = True
            await asyncio.sleep_ms(150)
            self._log_telemetry("parent", "lamp", {"action": "on"})
            self.step = self.STEP_DRAWING
            return
        # STEP_DRAWING -> STEP_LIGHT
        if self.step == self.STEP_DRAWING:
            self._log_telemetry("parent", "light_sensor", {"action": "triggered"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("parent", "mapping_video", {"action": "switch", "to": "reveal"})
            self.step = self.STEP_LIGHT
            return
        # STEP_LIGHT -> STEP_CAGE -> STEP_DONE
        if self.step == self.STEP_LIGHT:
            self._log_telemetry("child", "cage_rfid", {"action": "detected", "tag": "CAGE_A"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("child", "cage_rfid", {"action": "correct", "tag": "CAGE_A"})
            self.step = self.STEP_CAGE
            # Send cage_is_on_monster=True
            await asyncio.sleep_ms(150)
            await self.send_rift_json(cage_is_on_monster=True)
            # Auto-progress to DONE
            await asyncio.sleep_ms(150)
            self._log_telemetry("child", "servo_trap", {"action": "open"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("parent", "servo_trap", {"action": "open"})
            await asyncio.sleep_ms(150)
            self._log_telemetry("system", "workshop", {"action": "finished"})
            self.step = self.STEP_DONE
            self.logger.info("Workshop finished (waiting for final Rift JSON send)")
            return

    async def reset(self, by="server_reset"):
        """
        Reset internal state
        """
        self.step = self.STEP_IDLE
        self._session_done_reported = False
        self.state_initialized = False
        self._last_children_count = 0
        self._last_parent_count = 0
        self._last_payload = None
        self.torch_scanned_sent = False

        self.logger.info("Lost workshop reset")

    def _log_telemetry(self, room: str, event: str, payload: dict):
        """
        Internal helper to log what used to be WebSocket telemetry
        """
        self.logger.debug("[TELEMETRY] room={} event={} payload={}".format(room, event, payload))