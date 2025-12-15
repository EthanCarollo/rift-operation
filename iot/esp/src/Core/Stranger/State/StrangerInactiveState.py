from src.Core.Controller.StrangerController import StrangerActiveState, StrangerControllerState

class StrangerInactiveState(StrangerControllerState):
    def process_json_message(self, json):
        if json["start_system"] is not None and json["start_system"] == True:
            self.controller.swap_state(StrangerActiveState(self.controller))

    def update(self):
        pass