from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState

class StrangerInactiveState(StrangerControllerState):
    def process_json_message(self, json):
        if json["start_system"] is not None and json["start_system"] == True:
            from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
            self.controller.swap_state(StrangerActiveState(self.controller))

    def update(self):
        pass