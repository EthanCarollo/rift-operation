from src.Core.Controller.StrangerController import StrangerController

class StrangerControllerState:
    def __init__(self, controller: StrangerController):
        self.controller: StrangerController = controller
        pass

    def process_json_message(self, json):
        pass

    def update(self):
        pass