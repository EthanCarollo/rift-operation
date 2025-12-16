from src.Framework.Button.Button import Button, ButtonDelegate
from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState

"""
Not really used atm, but used to test after all in fact
"""
class StrangerWebSocketButtonDelegate(ButtonDelegate):
    def __init__(self, controller_state: StrangerControllerState):
        self.controller_state = controller_state

    def on_click(self):
        print("Recognize button")
        self.controller_state.recognize_stranger()