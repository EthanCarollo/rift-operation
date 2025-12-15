from src.Framework.Button.Button import Button, ButtonDelegate
from src.Framework.EspController import EspController

class StrangersWebSocketButtonDelegate(ButtonDelegate):
    def __init__(self, controller: EspController):
        self.controller = controller

    def on_click(self):
        print("clicked on button")