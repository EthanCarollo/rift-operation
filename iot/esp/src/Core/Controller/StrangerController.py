import ujson as json
from src.Framework.EspController import EspController
from src.Framework.Button.Button import Button
from src.Core.Stranger.StrangerWebSocketButtonDelegate import StrangerWebSocketButtonDelegate
from src.Core.Stranger.State import StrangerInactiveState, StrangerControllerState
from src.Framework.Config import Config

class StrangerController(EspController):
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger.name = "StrangerController"

        self.state: StrangerControllerState = StrangerInactiveState(self)
        
        self.button1: Button = Button(17, StrangerWebSocketButtonDelegate(self))

    def swap_state(self, state: StrangerControllerState):
        self.state = state

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            self.state.process_json_message(json= data)
        except Exception as e:
            # Temporary disable that
            pass

    async def update(self):
        self.state.update()