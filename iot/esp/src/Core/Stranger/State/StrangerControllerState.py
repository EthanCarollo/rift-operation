import asyncio

from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData


class StrangerControllerState:
    def __init__(self, controller):
        self.controller = controller
        pass

    def process_json_message(self, json):
        pass

    def update(self):
        pass

    def send_state(self, state_name):
        self.controller.logger.debug("send state name:" + state_name)

        msg = RiftOperationJsonData(
            stranger_state=state_name
        ).to_json()

        # DIRECT SEND (blocking, fast)
        self.controller.websocket_client.send_now(msg)