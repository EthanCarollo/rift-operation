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
        asyncio.run(self.controller.websocket_client.send(
            RiftOperationJsonData(
                device_id= self.controller.config.device_id,
                stranger_state= state_name
            ).to_json()
        ))