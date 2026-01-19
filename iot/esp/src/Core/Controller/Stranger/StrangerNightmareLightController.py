from src.Framework.EspController import EspController
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController
import ujson as json

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
    asyncio.sleep_ms = lambda ms: asyncio.sleep(ms/1000)

class StrangerDreamLightController(EspController):
    def __init__(self, config):
        super().__init__(config, "StrangerLightController")
        self.logger.name = "StrangerLightController"
        
        self.led_pin = 14
        self.led_pin_2 = 12
        self.led_count = 21
        self.led_count_2 = 21

        self.led_strip = LedStrip(self.led_pin, self.led_count)
        self.led_strip.clear()
        self.led_controller = LedController(self.led_strip)

        self.led_strip_2 = LedStrip(self.led_pin_2, self.led_count_2)
        self.led_strip_2.clear()
        self.led_controller_2 = LedController(self.led_strip_2)
        # self.led_controller.start_thread()
        self.led_controller.play_from_json("data/stranger/led_inactive.json")
        self.led_controller_2.play_from_json("data/stranger/led_inactive.json")
        # State to Animation mapping
        self.animation_map = {
            "inactive": "data/stranger/led_inactive.json",
            "active": "data/stranger/led_active.json",
            "step_2": "data/stranger/led_step2.json",
            "step_3": "data/stranger/led_step3.json",
            "step_4": "data/stranger/led_step4.json",
            "recognized": "data/stranger/led_end.json"
        }

    async def process_message(self, message):
        try:
            data = json.loads(message)
            
            # Handle brightness updates
            if "brightness" in data:
                brightness = float(data["brightness"])
                self.led_controller.set_brightness(brightness)
                self.led_controller_2.set_brightness(brightness)
                self.logger.info(f"Setting global brightness to: {brightness}")

            # Handle state changes for animations
            if "stranger_state" in data:
                state = data["stranger_state"]
                if state in self.animation_map:
                    anim_file = self.animation_map[state]
                    self.logger.info(f"Playing animation for state: {state} ({anim_file})")
                    self.led_controller.play_from_json(anim_file)
                    self.led_controller_2.play_from_json(anim_file)
                else:
                    self.logger.warning(f"Unknown stranger_state: {state}")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def update(self):
        # LedController thread handles animations, but we might need occasional updates
        self.led_controller.update()
        self.led_controller_2.update()
        asyncio.sleep_ms(50)


