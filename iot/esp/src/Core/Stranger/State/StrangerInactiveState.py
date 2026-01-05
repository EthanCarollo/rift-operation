from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
import asyncio

from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData


class StrangerInactiveState(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("inactive")

    def process_json_message(self, json):
        if json["start_system"] is not None and json["start_system"] == True:
            from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
            self.controller.swap_state(StrangerActiveState(self.controller))

    def update(self):
        pass