import ujson as json
from src.Framework.Config.Config import Config
from src.Framework.EspController import EspController
from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController

class StrangerNightmareController(EspController):
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger.name = "StrangerController"

        self.swap_state(StrangerActiveState(self))
        self.led_strip: LedStrip = LedStrip(25, 22)
        self.led_controller: LedController = LedController(self.led_strip)
        self.led_controller.play_from_json("data/stranger/led_anim_inactive.json")

    def swap_state(self, state):
        self.logger.debug(f"Swapping to StrangerController to new state : {state.__class__.__name__}")
        self.state = state

    async def process_message(self, message):
        try:
            data = json.loads(message)
            # self.logger.info(f"Received message: {data}")
            self.state.process_json_message(json= data)
        except Exception as e:
            # Temporary disable that
            pass

    async def update(self):
        self.state.update()