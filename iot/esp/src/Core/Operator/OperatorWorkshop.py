
import uasyncio as asyncio
import ujson as json
import src.Core.Operator.OperatorConstants as OC
from src.Core.Operator.State.OperatorStateIdle import OperatorStateIdle

class OperatorWorkshop:
    def __init__(self, controller):
        self.controller = controller
        self.logger = controller.logger # Use controller's logger directly to avoid extra wrapper
        self.hardware = None
        self.state = None
        self._last_payload = {}
        
        # Rift Button Logic State
        self.rift_button_ready = False # True if LED is ON and waiting for press
        self.current_rift_step = 0 # 1, 2, or 3
        
        # Start in Idle
        asyncio.create_task(self.swap_state(OperatorStateIdle(self)))

    def attach_hardware(self, hardware):
        self.hardware = hardware
        self.hardware.attach_workshop(self)

    async def swap_state(self, new_state):
        if self.state:
            await self.state.exit()
        self.state = new_state
        await self.state.enter()

    # --- Hardware Events ---
    def on_button_press(self, button_type):
        self.logger.info(f"Button Pressed: {button_type}")
        if button_type == "rift":
            asyncio.create_task(self.handle_rift_button())
        elif button_type == "battle":
            if self.state:
                asyncio.create_task(self.state.handle_button("battle"))

    def on_rfid_read(self, uid):
        self.logger.info(f"RFID Read: {uid}")
        if self.state:
            asyncio.create_task(self.state.handle_rfid(uid))

    async def handle_rift_button(self):
        # Only act if the button is "Ready" (LED is ON)
        if self.rift_button_ready:
            self.logger.info(f"Rift Closure Step {self.current_rift_step} Triggered!")
            
            # Construct payload dependent on the step
            payload_key = f"operator_launch_close_rift_step_{self.current_rift_step}"
            update = {payload_key: True}
            
            # Send updated payload
            await self.send_json(update)
            
            # Reset Button State
            self.rift_button_ready = False
            if self.hardware and self.hardware.rift_button:
                self.hardware.rift_button.turn_off()

    # --- WebSocket Handling ---
    async def process_message(self, message: str):
        try:
            data = json.loads(message)
            payload = data.get("value", data) if isinstance(data, dict) else data
        except Exception:
            return

        if not isinstance(payload, dict):
            return

        self._last_payload = payload
        
        # Global Reset
        if payload.get("reset_system") is True:
            await self.reset()
            return

        # 1. Rift Button Logic (Global)
        await self.check_rift_status(payload)

        # 2. Battle State Logic (State Transition)
        # Check if we need to enter Battle Mode
        # User said: "tant qu'on est pas dans rift_part_count=4, il passe à l'état idle"
        # So loop: if count >= 4 and not in BattleState -> Enter BattleState?
        # Or maybe check if specific keys are present?
        # Let's rely on rift_part_count for now.
        count = payload.get("rift_part_count", 0)
        if count >= 4 and self.state.step_id == OC.OperatorSteps.IDLE:
             from src.Core.Operator.State.OperatorStateBattle import OperatorStateBattle
             await self.swap_state(OperatorStateBattle(self))

        # Delegate to current state
        if self.state:
            await self.state.handle_message(payload)

    async def check_rift_status(self, payload):
        # Check for rift_part_count 2, 4, 6
        # Logic: "quand on recoit pour la première fois ... on allume la led"
        # We need to track if we already did it for this step? 
        # Or checks if the "step_X" is NOT true yet?
        # Yes: if count=2 and step_1 is False -> Turn LED ON.
        
        count = payload.get("rift_part_count", 0)
        
        step_to_trigger = 0
        if count == 2: step_to_trigger = 1
        elif count == 4: step_to_trigger = 2
        elif count == 6: step_to_trigger = 3
        
        if step_to_trigger > 0:
            # Check if this step is already done
            done_key = f"operator_launch_close_rift_step_{step_to_trigger}"
            is_done = payload.get(done_key, False)
            
            if not is_done and not self.rift_button_ready:
                # Need to perform action!
                self.current_rift_step = step_to_trigger
                self.rift_button_ready = True
                if self.hardware and self.hardware.rift_button:
                    self.hardware.rift_button.turn_on()
            
            elif is_done and self.rift_button_ready and self.current_rift_step == step_to_trigger:
                 # It's done, ensure LED is off (just in case)
                 self.rift_button_ready = False
                 if self.hardware and self.hardware.rift_button:
                    self.hardware.rift_button.turn_off()

    async def send_json(self, updates=None):
        if not self._last_payload:
            return
            
        payload = dict(self._last_payload)
        payload["device_id"] = self.controller.config.device_id
        
        if updates:
            payload.update(updates)
            
        try:
            # self.logger.info(f"Sending: {updates}")
            await self.controller.websocket_client.send(json.dumps(payload))
        except Exception as e:
            self.controller.logger.error(f"Send failed: {e}")

    async def reset(self):
        self.rift_button_ready = False
        self.current_rift_step = 0
        if self.hardware:
            if self.hardware.rift_button: self.hardware.rift_button.turn_off()
            if self.hardware.battle_button: self.hardware.battle_button.turn_off()
        await self.swap_state(OperatorStateIdle(self))
