"""
LostWorkshop.py - Business logic for the LOST workshop
"""
import uasyncio as asyncio
import ujson as json
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostLogger import LostLogger
from src.Core.Lost.State.LostStateIdle import LostStateIdle

class LostWorkshop:
    def __init__(self, controller):
        self.controller = controller
        # Delegate logging to a dedicated helper, using controller's logger
        self.logger = LostLogger(controller.logger)
        self.hardware = None
        # State & Config
        self.current_step_delay = LC.LostGameConfig.DEFAULT_STEP_DELAY
        self._last_payload = None
        self._state_data = {"torch": None, "cage": None}
        self.light_triggered = False
        self.state = None
        # Initialize State
        asyncio.create_task(self.swap_state(LostStateIdle(self)))

    def attach_hardware(self, hardware):
        self.hardware = hardware

    def on_rfid_read(self, uid):
        self.logger.info(f"Workshop Lost RFID: {uid}")
        if self.state and hasattr(self.state, "handle_rfid"):
             asyncio.create_task(self.state.handle_rfid(uid))

    def on_distance_event(self, distance, name):
        if self.state and hasattr(self.state, "handle_distance"):
             asyncio.create_task(self.state.handle_distance(distance))

    def on_servo_event(self, angle, name):
        if self.state and hasattr(self.state, "handle_servo"):
             asyncio.create_task(self.state.handle_servo(angle))

    async def swap_state(self, new_state):
        try:
            old_step = self.state.step_id if self.state else -1
            self.state = new_state
            
            if old_step != self.state.step_id and old_step != -1:
                self.logger.log_transition(old_step, self.state.step_id)
            
            await self.state.enter()
        except Exception as e:
            self.controller.logger.error(f"Error in swap_state: {e}")

    async def handle_short_press(self):
        if self.state:
            await self.state.handle_button()

    async def process_message(self, message: str):
        try:
            data = json.loads(message)
        except Exception:
            return

        payload = data.get("value", data) if isinstance(data, dict) else data
        if not isinstance(payload, dict):
            return
            
        # Handle signals
        if payload.get("signal") == "light_sensor_triggered":
            self.light_triggered = True
            if self.state:
                await self.state.handle_signal("light_sensor_triggered")
            return

        if "dream_rift_part_count" not in payload and "nightmare_rift_part_count" not in payload:
            return
        self._last_payload = payload
        
        # Fast-forward triggers
        if payload.get("cage_is_on_monster") is True:
             if self.state and LC.LostSteps.IDLE < self.state.step_id < LC.LostSteps.DONE:
                 await self.state.fast_forward_to(LC.LostSteps.DONE)
                 return

        if self.state:
            await self.state.handle_message(payload)

    async def send_rift_json(self, torch=None, cage=None):
        if not self._last_payload:
            self.controller.logger.error("Cannot send: no payload received")
            return

        if torch is not None: self._state_data["torch"] = torch
        if cage is not None: self._state_data["cage"] = cage

        payload = dict(self._last_payload)
        payload["device_id"] = self.controller.config.device_id
        
        for key, val in [("torch_scanned", self._state_data["torch"]),
                         ("cage_is_on_monster", self._state_data["cage"])]:
            if val is not None:
                payload[key] = val
        
        self._last_payload = payload

        try:
            self.logger.log_ws("torch={}, cage={}".format(
                self._state_data["torch"], self._state_data["cage"]
            ))
            await self.controller.websocket_client.send(json.dumps(payload))
        except Exception as e:
            self.controller.logger.error("Send failed: {}".format(e))

    async def reset(self):
        self._state_data = {"torch": None, "cage": None}
        self.light_triggered = False
        self.controller.logger.info("Lost workshop reset")
        await self.swap_state(LostStateIdle(self))
