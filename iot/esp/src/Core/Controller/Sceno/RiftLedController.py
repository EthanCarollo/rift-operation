import gc
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


class RiftLedController(EspController):
    def __init__(self, config: Config):
        super().__init__(config, "RiftLedController")

        self.led_pin = 14
        self.led_count = 88

        self.led_strip = LedStrip(self.led_pin, self.led_count)
        self.led_strip.clear()
        self.led_controller = LedController(self.led_strip)

        self.led_controller.play_from_json("data/rift/classic_anim.json")
        
        self.last_rift_part_count = None
        self.blink_playing = False
        self.gc_counter = 0

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            
            rift_part_count = data.get("rift_part_count")
            
            if rift_part_count is not None and rift_part_count != self.last_rift_part_count:
                self.logger.info(f"🎬 rift_part_count changed to {rift_part_count} - Playing blink animation")
                self.led_controller.play_from_json("data/rift/blink_anim.json", loop=False)
                self.blink_playing = True
                self.last_rift_part_count = rift_part_count
                gc.collect()
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def update(self):
        self.led_controller.update()
        
        if self.blink_playing and not self.led_controller.is_playing:
            self.logger.info("✨ Blink finished - Replaying classic animation")
            self.led_controller.play_from_json("data/rift/classic_anim.json")
            self.blink_playing = False
            gc.collect()
        
        # Periodic garbage collection every 100 updates
        self.gc_counter += 1
        if self.gc_counter >= 100:
            gc.collect()
            self.gc_counter = 0
        
        asyncio.sleep_ms(50)
