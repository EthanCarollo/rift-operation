import ujson as json
from src.Framework.EspController import EspController
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController
from src.Framework.Config import Config

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
    asyncio.sleep_ms = lambda ms: asyncio.sleep(ms/1000)

"""
Here we will need to put new led light for this kind of shit
"""
class RiftLedController(EspController):
    def __init__(self, config: Config):
        super().__init__(config, "RiftLedController")

        self.led_pin = 14
        self.led_count = 88

        self.led_strip = LedStrip(self.led_pin, self.led_count)
        self.led_strip.clear()
        self.led_controller = LedController(self.led_strip)

        self.led_controller.play_from_json("data/rift/classic_anim.json")


    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            # Handle it
        except Exception as e:
            # Temporary disable that
            pass

    async def update(self):
        self.led_controller.update()
        asyncio.sleep_ms(50)
