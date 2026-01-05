import uasyncio as asyncio
import ujson as json
from src.Framework.EspController import EspController
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController as FrameworkLedController

class DreamLedController(EspController):
    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "DreamLedController"
        
        # Hardware Configuration (Hardcoded as per plan)
        self.led_pin = 4
        self.led_count = 20
        
        self.strip = LedStrip(self.led_pin, self.led_count)
        self.strip.clear()
        self.led_controller = FrameworkLedController(self.strip)
        self.led_controller.start_thread()

        self.state = {}
        self.current_anim_state = None
        
        # State to Animation Mapping
        self.anim_mapping = {
            "step_1_dream_success": "data/depth/dream/step1_success.json",
            "step_2_dream_success": "data/depth/dream/step2_success.json",
            "step_3_dream_success": "data/depth/dream/step3_success.json",
            "victory": "data/depth/dream/anim_victory.json",
            "idle": "data/depth/dream/anim_idle.json",
            "default": "data/depth/dream/step_default.json"
        }

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.state = data
            # self.logger.info("📡 State received") 
        except Exception as e:
            self.logger.error(f"Invalid JSON: {e}")

    async def update(self):
        # Check depth_state
        depth_state = self.state.get("depth_state", "default")
        
        # Only switch animation if state changed
        if depth_state != self.current_anim_state:
            self.logger.info(f"🔄 State Changed: {self.current_anim_state} -> {depth_state}")
            self.current_anim_state = depth_state
            
            anim_file = self.anim_mapping.get(depth_state)
            if not anim_file:
                self.logger.warn(f"⚠️ No mapping for state '{depth_state}', using default.")
                anim_file = self.anim_mapping.get("default")
            
            if anim_file:
                self.logger.info(f"🎬 Playing: {anim_file}")
                # play_from_json handles 'stop' implicitly by starting a new one? 
                # Checking LedController: calling play overwrites previous.
                self.led_controller.play_from_json(anim_file, loop=False)
        
        await asyncio.sleep(0.1)

