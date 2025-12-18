from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
import asyncio

class StrangerInactiveState(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)

        self.controller.led_controller.play_from_json("data/stranger/led_anim_inactive.json")

    def process_json_message(self, json):
        if json["start_system"] is not None and json["start_system"] == True:
            from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
            self.controller.swap_state(StrangerActiveState(self.controller))

    def update(self):
        pass