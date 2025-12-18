import ujson as json
from src.Framework.Config.Config import Config
from src.Framework.EspController import EspController
from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController

class StrangerNightmareController(EspController):
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger.name = "StrangerController"
        self.led_strip: LedStrip = LedStrip(13, 32)
        self.led_controller: LedController = LedController(self.led_strip)
        self.led_controller.start_thread()

        self.swap_state(StrangerInactiveState(self))

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