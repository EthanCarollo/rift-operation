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
    STEP_IDLE, STEP_ACTIVE, STEP_DISTANCE, STEP_DRAWING, STEP_LIGHT, STEP_CAGE, STEP_DONE = 0, 1, 2, 3, 4, 5, 7
    STEP_NAMES = {0: "IDLE", 1: "ACTIVE", 2: "DISTANCE", 3: "DRAWING", 4: "LIGHT", 5: "CAGE", 7: "DONE"}
    
    # --- Target counts to auto-start ---
    TARGET_CHILDREN_COUNT = 2
    TARGET_PARENT_COUNT   = 2

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"

        self.step = self.STEP_IDLE
        # Store the last received payload to modify and resend
        self._last_payload = None
        # Local state for the values we send
        self._local_torch_scanned = None
        self._local_cage_is_on_monster = None
        self._local_preset_lost = None
        # Hardware button (GPIO 27)
        self.button = Button(pin_id=27, delegate=LostButtonDelegate(self))

    def _log_step_transition(self, from_step, to_step):
        """Log a step transition with visual separators"""
        from_name = self.STEP_NAMES.get(from_step, str(from_step))
        to_name = self.STEP_NAMES.get(to_step, str(to_step))
        self.logger.info("-------- {} -> {} --------".format(from_name, to_name))

    def _log_ws_send(self, message):
        """Log WebSocket send with visual separators"""
        self.logger.debug("-------------------------------")
        self.logger.debug("WS SEND: {}".format(message))
        self.logger.debug("-------------------------------")

    async def send_rift_json(self, torch_scanned=None, cage_is_on_monster=None, preset_lost=None):
        """
        Modify the last received payload with the specified values and send it back
        """
        if self._last_payload is None:
            self.logger.error("Cannot send Rift JSON: no payload received yet")
            return

        # Update local state with new values
        if torch_scanned is not None:
            self._local_torch_scanned = torch_scanned
        if cage_is_on_monster is not None:
            self._local_cage_is_on_monster = cage_is_on_monster
        if preset_lost is not None:
            self._local_preset_lost = preset_lost

        # Copy the last payload
        payload_to_send = dict(self._last_payload)
        # Change device_id to our own
        payload_to_send["device_id"] = self.config.device_id
        
        # Always include ALL our local state values
        if self._local_torch_scanned is not None:
            payload_to_send["torch_scanned"] = self._local_torch_scanned
        if self._local_cage_is_on_monster is not None:
            payload_to_send["cage_is_on_monster"] = self._local_cage_is_on_monster
        if self._local_preset_lost is not None:
            payload_to_send["preset_lost"] = self._local_preset_lost

        try:
            json_str = json.dumps(payload_to_send)
            self._log_ws_send("torch={}, cage={}, preset_lost={}".format(
                payload_to_send.get("torch_scanned"),
                payload_to_send.get("cage_is_on_monster"),
                payload_to_send.get("preset_lost")
            ))
            await self.websocket_client.send(json_str)
        except Exception as e:
            self.logger.error("Failed to send Rift JSON: {}".format(e))

    async def process_message(self, message: str):
        """
        Handle Rift JSON broadcast from the server.
        Auto-starts workshop when children=2 and parent=2.
        """
        try:
            data = json.loads(message)
        except Exception:
            return

        payload = data.get("value") if isinstance(data, dict) and "value" in data else data
        if not isinstance(payload, dict):
            return

        # Check if this is the Rift JSON we care about
        if "children_rift_part_count" not in payload and "parent_rift_part_count" not in payload:
            return
        
        # Store the full payload for later modification
        self._last_payload = payload
        
        # Get counts from payload
        children = payload.get("children_rift_part_count")
        parent = payload.get("parent_rift_part_count")
        
        # Auto-start: trigger immediately when we receive 2/2 and we're IDLE
        if (self.step == self.STEP_IDLE and 
            children == self.TARGET_CHILDREN_COUNT and 
            parent == self.TARGET_PARENT_COUNT):
            await self.start(by="rift_json")

    async def update(self):
        """
        Called repeatedly by EspController.main()
        Nothing to do here - everything is event-driven now.
        """
        pass

    async def start(self, by="server_start"):
        """
        Start Lost workshop scenario
        """
        if self.step != self.STEP_IDLE:
            return

        old_step = self.step
        self.step = self.STEP_ACTIVE
        # Reset local state for new session
        self._local_torch_scanned = None
        self._local_cage_is_on_monster = None
        self._local_preset_lost = None

        self.logger.info("LOST Started")
        self._log_step_transition(old_step, self.step)
        await self.send_rift_json(preset_lost=True)
        await asyncio.sleep_ms(150)
        self._log_telemetry("system", "workshop", "start", "ON")
        await asyncio.sleep_ms(150)
        self._log_telemetry("parent", "speaker", "audio", "ON")
        await asyncio.sleep_ms(150)
        self._log_telemetry("child", "animals_led", "led", "ON")

    async def handle_short_press(self):
        """
        Called by LostButtonDelegate when the hardware button is pressed shortly
        """
        if self.step == self.STEP_DONE:
            return

        self.logger.info("BTN action: next_step")
        await asyncio.sleep_ms(250)
        await self.next_step()

    async def next_step(self):
        """
        Progress through workshop steps
        """
        old_step = self.step
        
        # STEP_ACTIVE -> STEP_DISTANCE
        if self.step == self.STEP_ACTIVE:
            self.step = self.STEP_DISTANCE
            self._log_step_transition(old_step, self.step)
            self._log_telemetry("child", "distance_sensor", "sensor", "TRIGGERED")
            await asyncio.sleep_ms(250)
            self._log_telemetry("child", "llm", "ia", "TRIGGERED")
            await asyncio.sleep_ms(250)
            self._log_telemetry("child", "speaker", "audio", "ON")
            return
            
        # STEP_DISTANCE -> STEP_DRAWING
        if self.step == self.STEP_DISTANCE:
            self.step = self.STEP_DRAWING
            self._log_step_transition(old_step, self.step)
            self._log_telemetry("child", "drawing", "camera", "READ")
            await asyncio.sleep_ms(250)
            self._log_telemetry("child", "llm", "ia", "TRIGGERED")
            await asyncio.sleep_ms(250)
            self._log_telemetry("child", "drawing", "ia", "RECOGNIZED: flashlight")
            await asyncio.sleep_ms(250)
            await self.send_rift_json(torch_scanned=True)
            await asyncio.sleep_ms(250)
            self._log_telemetry("parent", "lamp", "led", "ON")
            return
            
        # STEP_DRAWING -> STEP_LIGHT
        if self.step == self.STEP_DRAWING:
            self.step = self.STEP_LIGHT
            self._log_step_transition(old_step, self.step)
            self._log_telemetry("parent", "light_sensor", "sensor", "TRIGGERED")
            await asyncio.sleep_ms(250)
            self._log_telemetry("parent", "mapping_video", "video", "SWITCH: reveal")
            return
            
        # STEP_LIGHT -> STEP_CAGE -> STEP_DONE
        if self.step == self.STEP_LIGHT:
            self.step = self.STEP_CAGE
            self._log_step_transition(old_step, self.step)
            self._log_telemetry("child", "cage", "rfid", "DETECTED: CAGE_A")
            await asyncio.sleep_ms(250)
            self._log_telemetry("child", "cage", "rfid", "CORRECT")
            await asyncio.sleep_ms(250)
            await self.send_rift_json(cage_is_on_monster=True)
            await asyncio.sleep_ms(250)
            # Progress to DONE
            old_step = self.step
            self.step = self.STEP_DONE
            self._log_step_transition(old_step, self.step)
            self._log_telemetry("child", "servo_trap", "servo", "OPEN")
            await asyncio.sleep_ms(250)
            self._log_telemetry("parent", "servo_trap", "servo", "OPEN")
            await asyncio.sleep_ms(250)
            self._log_telemetry("system", "workshop", "state", "FINISHED")
            # Send final JSON right here (not in update())
            self.logger.info("Workshop finished, sending final Rift JSON")
            await self.send_rift_json(
                torch_scanned=True,
                cage_is_on_monster=True,
                preset_lost=False
            )
            return

    async def reset(self, by="server_reset"):
        """
        Reset internal state
        """
        self.step = self.STEP_IDLE
        self._last_payload = None
        self._local_torch_scanned = None
        self._local_cage_is_on_monster = None
        self._local_preset_lost = None
        self.logger.info("Lost workshop reset")

    def _log_telemetry(self, room: str, decoration: str, module: str, action: str):
        """
        Log telemetry in human-readable format
        """
        room_display = "Parent" if room == "parent" else "Enfant" if room == "child" else "System"
        self.logger.debug("Room: {} | Deco: {} | Module: {} | Action: {}".format(
            room_display, decoration, module, action
        ))