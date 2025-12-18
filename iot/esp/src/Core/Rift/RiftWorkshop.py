"""
RiftWorkshop - Business logic for the RIFT workshop
"""
import ujson as json
from src.Core.Rift.RiftState import RiftState

class RiftWorkshop:
    def __init__(self, controller):
        self.controller = controller
        self.logger = controller.logger
        self.hardware = None

        self.state = None
        self._last_payload = None

        self.scanned_dream_slots = set()

    def attach_hardware(self, hardware):
        self.hardware = hardware

    def init_state(self):
        if self.state is None:
            self.state = RiftState(self)
            self.state.enter()

    def on_rfid_read(self, uid, reader_name):
        if self.state:
            self.state.on_rfid_read(uid, reader_name)

    def on_rfid_lost(self, uid, reader_name):
        if self.state:
            self.state.on_rfid_lost(uid, reader_name)

    async def process_message(self, message: str):
        try:
            data = json.loads(message)
        except Exception:
            return

        payload = data.get("value", data) if isinstance(data, dict) else None
        if not isinstance(payload, dict):
            return

        self._last_payload = payload
        self.state.process_json_message(payload)

    async def send_counts(self):
        payload = dict(self._last_payload) if self._last_payload else {}

        payload["device_id"] = self.controller.config.device_id
        payload["children_rift_part_count"] = len(self.scanned_dream_slots)
        # payload["parent_rift_part_count"] = ...

        await self.controller.websocket_client.send(json.dumps(payload))

    async def reset(self):
        self.scanned_dream_slots.clear()
        self.state = RiftState(self)
        self.state.enter()
