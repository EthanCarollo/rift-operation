"""
BattleWorkshop.py - Business logic for the BATTLE workshop
"""
import uasyncio as asyncio
import ujson as json
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleLogger import BattleLogger
from src.Core.Battle.State.BattleStateIdle import BattleStateIdle


class BattleWorkshop:
    def __init__(self, controller):
        self.controller = controller
        self.logger = BattleLogger(controller.logger)
        self.hardware = None
        
        # Game State
        self.current_hp = BC.BattleGameConfig.TOTAL_HP
        self.current_round = 0
        self.current_attack = None
        self.counter_valid = False   # This ESP's counter validation
        self.button_ready = False    # Button is lit and ready to press
        
        # WebSocket state
        self._last_payload = None
        self.state = None
        
        # Initialize to Idle state
        asyncio.create_task(self.swap_state(BattleStateIdle(self)))

    def attach_hardware(self, hardware):
        """Attach hardware wrapper"""
        self.hardware = hardware

    def on_rfid_read(self, uid):
        """Called when RFID tag is detected"""
        self.logger.info(f"RFID detected: {uid}")
        if self.state and hasattr(self.state, "handle_rfid"):
            asyncio.create_task(self.state.handle_rfid(uid))

    async def handle_short_press(self):
        """Called when arcade button is pressed"""
        self.logger.info("Button pressed!")
        if self.state:
            await self.state.handle_button()

    async def swap_state(self, new_state):
        """Transition to a new state"""
        try:
            old_step = self.state.step_id if self.state else -1
            
            if self.state:
                await self.state.exit()
                
            self.state = new_state
            
            if old_step != self.state.step_id and old_step != -1:
                self.logger.log_transition(old_step, self.state.step_id)
            
            await self.state.enter()
        except Exception as e:
            self.controller.logger.error(f"Error in swap_state: {e}")

    async def process_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
        except Exception:
            return

        payload = data.get("value", data) if isinstance(data, dict) else data
        if not isinstance(payload, dict):
            return
            
        # Global Reset Logic
        if payload.get("reset_system") is True:
            self.controller.logger.info("Received reset_system command")
            await self.reset()
            return

        self._last_payload = payload
        
        if self.state:
            await self.state.handle_message(payload)

    async def send_battle_json(self, **kwargs):
        """
        Send battle state via WebSocket.
        
        Possible kwargs:
        - battle_state: str (current state name)
        - battle_hp: int (remaining HP)
        - battle_round: int (current round 1-5)
        - battle_attack: str (current boss attack)
        - battle_counter_valid_parent: bool
        - battle_counter_valid_child: bool
        - battle_button_ready_parent: bool
        - battle_button_ready_child: bool
        - battle_cage_parent: bool (RFID cage detected)
        - battle_cage_child: bool
        - battle_video_play: str (video filename)
        - battle_music_play: str (music filename)
        """
        if not self._last_payload:
            self.controller.logger.error("Cannot send: no payload received yet")
            return

        payload = dict(self._last_payload)
        payload["device_id"] = self.controller.config.device_id
        
        # Add all provided battle fields
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        
        self._last_payload = payload

        try:
            self.logger.log_ws(f"Sending: {list(kwargs.keys())}")
            await self.controller.websocket_client.send(json.dumps(payload))
        except Exception as e:
            self.controller.logger.error(f"Send failed: {e}")

    async def reset(self):
        """Reset workshop to initial state"""
        self.current_hp = BC.BattleGameConfig.TOTAL_HP
        self.current_round = 0
        self.current_attack = None
        self.counter_valid = False
        self.button_ready = False
        
        if self.hardware:
            self.hardware.clear_leds()
            self.hardware.set_button_led(False)
        
        self.logger.info("Battle workshop reset")
        await self.swap_state(BattleStateIdle(self))

    def get_role_color(self):
        """Get the LED color based on role"""
        if self.hardware.role == "child":
            return BC.BattleLedColors.CHILD_PINK
        else:
            return BC.BattleLedColors.PARENT_BLUE
