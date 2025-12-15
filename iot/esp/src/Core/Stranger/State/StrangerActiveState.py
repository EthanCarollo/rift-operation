from src.Core.Controller.StrangerController import StrangerInactiveState, StrangerControllerState

class StrangerActiveState(StrangerControllerState):
    def process_json_message(self, json):
        # And also then call table to say its good and she is active
        
        if json["recognized_stranger_name"] is not None and json["recognized_stranger_name"] == True:
            self.controller.swap_state(StrangerInactiveState(self.controller))

    def update(self):
        pass