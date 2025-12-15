"""
LostController - ESP32 Controller for the LOST workshop

State Machine:
    IDLE -> ACTIVE -> DISTANCE -> DRAWING -> LIGHT -> CAGE -> DONE

Triggers:
    - Auto-starts when receiving JSON with children=2, parent=2
    - Button press advances to next step
"""

import ujson as json
import uasyncio as asyncio

from src.Framework.EspController import EspController
from src.Framework.Button.Button import Button
from src.Core.Lost.LostButtonDelegate import LostButtonDelegate


class LostController(EspController):
    """LOST workshop controller - manages the workshop state machine and WebSocket communication"""

    # State machine constants
    STEP_IDLE, STEP_ACTIVE, STEP_DISTANCE, STEP_DRAWING, STEP_LIGHT, STEP_CAGE, STEP_DONE = 0, 1, 2, 3, 4, 5, 7
    STEP_NAMES = {0: "IDLE", 1: "ACTIVE", 2: "DISTANCE", 3: "DRAWING", 4: "LIGHT", 5: "CAGE", 7: "DONE"}
    
    # Auto-start trigger values
    TARGET_COUNTS = (2, 2)  # (children, parent)
    
    # Timing constants (ms)
    STEP_DELAY = 250
    START_DELAY = 150

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "LostController"
        self._init_state()
        self.button = Button(pin_id=27, delegate=LostButtonDelegate(self))

    def _init_state(self):
        """Initialize/reset all state variables"""
        self.step = self.STEP_IDLE
        self._last_payload = None
        self._state = {"torch": None, "cage": None, "preset": None}

    # =========================================================================
    # LOGGING HELPERS
    # =========================================================================

    def _log_transition(self, from_step, to_step):
        """Log step transition with visual separator"""
        self.logger.info("-------- {} -> {} --------".format(
            self.STEP_NAMES.get(from_step, str(from_step)),
            self.STEP_NAMES.get(to_step, str(to_step))
        ))

    def _log_ws(self, msg):
        """Log WebSocket message with separators"""
        self.logger.debug("-------------------------------")
        self.logger.debug("WS SEND: {}".format(msg))
        self.logger.debug("-------------------------------")

    def _log_event(self, room, deco, module, action):
        """Log telemetry event in readable format"""
        rooms = {"parent": "Parent", "child": "Enfant", "system": "System"}
        self.logger.debug("Room: {} | Deco: {} | Module: {} | Action: {}".format(
            rooms.get(room, room), deco, module, action
        ))

    # =========================================================================
    # WEBSOCKET COMMUNICATION
    # =========================================================================

    async def send_rift_json(self, torch=None, cage=None, preset=None):
        """Send modified Rift JSON with updated state values"""
        if not self._last_payload:
            self.logger.error("Cannot send: no payload received")
            return

        # Update local state
        if torch is not None: self._state["torch"] = torch
        if cage is not None: self._state["cage"] = cage
        if preset is not None: self._state["preset"] = preset

        # Build payload
        payload = dict(self._last_payload)
        payload["device_id"] = self.config.device_id
        
        for key, val in [("torch_scanned", self._state["torch"]),
                         ("cage_is_on_monster", self._state["cage"]),
                         ("preset_lost", self._state["preset"])]:
            if val is not None:
                payload[key] = val

        try:
            self._log_ws("torch={}, cage={}, preset={}".format(
                self._state["torch"], self._state["cage"], self._state["preset"]
            ))
            await self.websocket_client.send(json.dumps(payload))
        except Exception as e:
            self.logger.error("Send failed: {}".format(e))

    async def process_message(self, message: str):
        """Handle incoming Rift JSON - auto-start if conditions met"""
        try:
            data = json.loads(message)
        except Exception:
            return

        payload = data.get("value", data) if isinstance(data, dict) else data
        if not isinstance(payload, dict):
            return

        # Only process Rift JSON
        if "children_rift_part_count" not in payload and "parent_rift_part_count" not in payload:
            return
        
        self._last_payload = payload
        counts = (payload.get("children_rift_part_count"), payload.get("parent_rift_part_count"))
        
        # Auto-start condition
        if self.step == self.STEP_IDLE and counts == self.TARGET_COUNTS:
            await self._start()

    async def update(self):
        """Main loop callback - not used (event-driven)"""
        pass

    # =========================================================================
    # STATE MACHINE
    # =========================================================================

    async def _start(self):
        """Start workshop session"""
        if self.step != self.STEP_IDLE:
            return

        old, self.step = self.step, self.STEP_ACTIVE
        self._state = {"torch": None, "cage": None, "preset": None}

        self.logger.info("LOST Started")
        self._log_transition(old, self.step)
        await self.send_rift_json(preset=True)
        
        await asyncio.sleep_ms(self.START_DELAY)
        self._log_event("system", "workshop", "start", "ON")
        await asyncio.sleep_ms(self.START_DELAY)
        self._log_event("parent", "speaker", "audio", "ON")
        await asyncio.sleep_ms(self.START_DELAY)
        self._log_event("child", "animals_led", "led", "ON")

    async def handle_short_press(self):
        """Button press handler - advance to next step"""
        if self.step == self.STEP_DONE:
            return
        self.logger.info("BTN action: next_step")
        await asyncio.sleep_ms(self.STEP_DELAY)
        await self._next_step()

    async def _next_step(self):
        """State machine - transition to next step"""
        old = self.step
        
        if self.step == self.STEP_ACTIVE:
            await self._step_distance(old)
        elif self.step == self.STEP_DISTANCE:
            await self._step_drawing(old)
        elif self.step == self.STEP_DRAWING:
            await self._step_light(old)
        elif self.step == self.STEP_LIGHT:
            await self._step_cage_and_done(old)

    async def _step_distance(self, old):
        """ACTIVE -> DISTANCE"""
        self.step = self.STEP_DISTANCE
        self._log_transition(old, self.step)
        self._log_event("child", "distance_sensor", "sensor", "TRIGGERED")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("child", "llm", "ia", "TRIGGERED")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("child", "speaker", "audio", "ON")

    async def _step_drawing(self, old):
        """DISTANCE -> DRAWING"""
        self.step = self.STEP_DRAWING
        self._log_transition(old, self.step)
        self._log_event("child", "drawing", "camera", "READ")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("child", "llm", "ia", "TRIGGERED")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("child", "drawing", "ia", "RECOGNIZED: flashlight")
        await asyncio.sleep_ms(self.STEP_DELAY)
        await self.send_rift_json(torch=True)
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("parent", "lamp", "led", "ON")

    async def _step_light(self, old):
        """DRAWING -> LIGHT"""
        self.step = self.STEP_LIGHT
        self._log_transition(old, self.step)
        self._log_event("parent", "light_sensor", "sensor", "TRIGGERED")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("parent", "mapping_video", "video", "SWITCH: reveal")

    async def _step_cage_and_done(self, old):
        """LIGHT -> CAGE -> DONE (final sequence)"""
        # CAGE
        self.step = self.STEP_CAGE
        self._log_transition(old, self.step)
        self._log_event("child", "cage", "rfid", "DETECTED: CAGE_A")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("child", "cage", "rfid", "CORRECT")
        await asyncio.sleep_ms(self.STEP_DELAY)
        await self.send_rift_json(cage=True)
        await asyncio.sleep_ms(self.STEP_DELAY)
        
        # DONE
        old, self.step = self.step, self.STEP_DONE
        self._log_transition(old, self.step)
        self._log_event("child", "servo_trap", "servo", "OPEN")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("parent", "servo_trap", "servo", "OPEN")
        await asyncio.sleep_ms(self.STEP_DELAY)
        self._log_event("system", "workshop", "state", "FINISHED")
        
        # Final JSON
        self.logger.info("Workshop finished, sending final Rift JSON")
        await self.send_rift_json(torch=True, cage=True, preset=False)

    async def reset(self):
        """Reset controller to initial state"""
        self._init_state()
        self.logger.info("Lost workshop reset")