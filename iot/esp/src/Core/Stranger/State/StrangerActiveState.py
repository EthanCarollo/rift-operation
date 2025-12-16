from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
from src.Core.Stranger.StrangerWebSocketButtonDelegate import StrangerWebSocketButtonDelegate
from src.Framework.Button.Button import Button

class StrangerActiveState(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.button1: Button = Button(17, StrangerWebSocketButtonDelegate(self))

    def process_json_message(self, json):
        pass

    def recognize_stranger(self):
        self.button1.deactivate()
        self.controller.logger.debug("Stranger has been recognized ! Good job !")
        from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
        self.controller.swap_state(StrangerInactiveState(self.controller))


    def update(self):
        pass