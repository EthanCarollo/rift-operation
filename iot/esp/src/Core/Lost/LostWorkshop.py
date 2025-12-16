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
        
        # State & Config
        self.current_step_delay = LC.DEFAULT_STEP_DELAY
        self._last_payload = None
        self._state_data = {"torch": None, "cage": None, "preset": None}
        self.state = None
        
        # Initialize State
        asyncio.create_task(self.swap_state(LostStateIdle(self)))

    async def swap_state(self, new_state):
        try:
            old_step = self.state.step_id if self.state else -1
            self.state = new_state
            
            if old_step != self.state.step_id:
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

        if "children_rift_part_count" not in payload and "parent_rift_part_count" not in payload:
            return
        
        self._last_payload = payload
        
        # Fast-forward triggers
        if payload.get("cage_is_on_monster") is True:
             if self.state and self.state.step_id < LC.STEP_DONE:
                 await self.fast_forward_to(LC.STEP_DONE)
                 return 
        
        elif payload.get("torch_scanned") is True:
             if self.state and self.state.step_id < LC.STEP_DRAWING:
                 await self.fast_forward_to(LC.STEP_DRAWING)
                 return

        if self.state:
            await self.state.handle_message(payload)

    async def fast_forward_to(self, target_step):
        if not self.state or self.state.step_id >= target_step:
            return

        self.controller.logger.info("FAST FORWARD -> {}".format(LC.STEP_NAMES.get(target_step, target_step)))
        
        original_delay = self.current_step_delay
        self.current_step_delay = 0
        
        try:
            # Loop until we catch up
            max_loops = 10
            while self.state.step_id < target_step and max_loops > 0:
                current_id = self.state.step_id
                await self.state.next_step()
                if self.state.step_id == current_id: # Stuck?
                    break
                max_loops -= 1
        finally:
            self.current_step_delay = original_delay

    async def send_rift_json(self, torch=None, cage=None, preset=None):
        if not self._last_payload:
            self.controller.logger.error("Cannot send: no payload received")
            return

        if torch is not None: self._state_data["torch"] = torch
        if cage is not None: self._state_data["cage"] = cage
        if preset is not None: self._state_data["preset"] = preset

        payload = dict(self._last_payload)
        payload["device_id"] = self.controller.config.device_id
        
        for key, val in [("torch_scanned", self._state_data["torch"]),
                         ("cage_is_on_monster", self._state_data["cage"]),
                         ("preset_lost", self._state_data["preset"])]:
            if val is not None:
                payload[key] = val

        try:
            self.logger.log_ws("torch={}, cage={}, preset={}".format(
                self._state_data["torch"], self._state_data["cage"], self._state_data["preset"]
            ))
            await self.controller.websocket_client.send(json.dumps(payload))
        except Exception as e:
            self.controller.logger.error("Send failed: {}".format(e))

    async def reset(self):
        self._state_data = {"torch": None, "cage": None, "preset": None}
        await self.swap_state(LostStateIdle(self))
        self.controller.logger.info("Lost workshop reset")
