import ujson as json
from src.Framework.Config.Config import Config
from src.Framework.EspController import EspController
from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState

class StrangerParentController(EspController):
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger.name = "StrangerController"

        self.swap_state(StrangerActiveState(self))

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