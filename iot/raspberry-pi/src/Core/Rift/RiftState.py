"""
RiftState - Unified state machine for RIFT workshop
"""
import asyncio
import json

from src.Core.Rift.RiftConstants import RiftSteps, RiftTags

class RiftState:
    def __init__(self, workshop):
        self.workshop = workshop
        self.logger = workshop.logger
        self.step = RiftSteps.IDLE
        # Validation flags for current step
        self._dream_valid = False
        self._nightmare_valid = False
        self._transitioning = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def enter(self):
        self._dream_valid = False
        self._nightmare_valid = False
        self._transitioning = False


    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------
    def process_json_message(self, data: dict):
        # Reset System handling
        if data.get("reset_system") is True:
            self.logger.info("Reset System command received")
            self._go_to_step(RiftSteps.STEP_1)
            return

        if self.step == RiftSteps.IDLE and data.get("start_system") is True:
            self._go_to_step(RiftSteps.STEP_1)

    # ------------------------------------------------------------------
    # RFID
    # ------------------------------------------------------------------
    def on_rfid_read(self, uid: str, reader_name: str):
        if self.step not in (
            RiftSteps.STEP_1,
            RiftSteps.STEP_2,
            RiftSteps.STEP_3,
        ):
            return

        self._handle_dream(uid, reader_name)
        self._handle_nightmare(uid, reader_name)

    def on_rfid_lost(self, uid, reader_name):
        pass

    # ------------------------------------------------------------------
    # Validation logic
    # ------------------------------------------------------------------
    def _handle_dream(self, uid: str, reader_name: str):
        expected_slot = f"DreamSlot{self.step}"
        expected_uid = RiftTags.DREAM.get(expected_slot)

        if reader_name != expected_slot:
            return

        if expected_uid == "XX-XX-XX-XX-XX":
            return

        if uid != expected_uid:
            self.logger.info(f"INVALID Dream tag on {reader_name} !")
            return

        if not self._dream_valid:
            self.logger.info(f"VALID Dream tag on {reader_name} !")
            self._dream_valid = True
            self.workshop.scanned_dream_slots.add(expected_slot)
            self._check_step_completion()

    def _handle_nightmare(self, uid: str, reader_name: str):
        expected_slot = f"NightmareSlot{self.step}"
        expected_uid = RiftTags.NIGHTMARE.get(expected_slot)

        if reader_name != expected_slot:
            return

        if expected_uid == "XX-XX-XX-XX-XX":
            return

        if uid != expected_uid:
            self.logger.info(f"INVALID Nightmare tag on {reader_name} !")
            return

        if not self._nightmare_valid:
            self.logger.info(f"VALID Nightmare tag on {reader_name} !")
            self._nightmare_valid = True
            self.workshop.scanned_nightmare_slots.add(expected_slot)
            self._check_step_completion()

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------
    def _check_step_completion(self):
        """
        Transition ONLY if all required tags for this step are validated
        """
        if self._transitioning:
            return

        if self._dream_valid and self._nightmare_valid:
            self.logger.info("Futur implementation : Allumage Led et Animations de la Rift")
            self.logger.info(f"All UUID Valid, {RiftSteps.get_name(self.step)} completed !")
            # Send updated counts only when both are valid
            asyncio.create_task(self.workshop.send_counts())
            self._transitioning = True
            asyncio.create_task(self._next_step())

    async def _next_step(self):
        await asyncio.sleep(0.5)

        if self.step == RiftSteps.STEP_3:
            self._go_to_step(RiftSteps.DONE)
        else:
            self._go_to_step(self.step + 1)

    def _go_to_step(self, step: int):
        old_name = RiftSteps.get_name(self.step)
        new_name = RiftSteps.get_name(step)
        self.logger.info(f"-------- {old_name} -> {new_name} ---------")
        self.logger.info(f"Waiting scan RIFT parts...")

        self.step = step
        self.enter()

        if step == RiftSteps.DONE:
            asyncio.create_task(self._send_end_system())

    # ------------------------------------------------------------------
    # End system
    # ------------------------------------------------------------------
    async def _send_end_system(self):
        payload = dict(self.workshop._last_payload) if self.workshop._last_payload else {}

        payload["device_id"] = self.workshop.controller.config.device_id
        payload["end_system"] = True
        payload["rift_part_count"] = ( len(self.workshop.scanned_dream_slots) + len(self.workshop.scanned_nightmare_slots))

        try:
            await self.workshop.controller.websocket_client.send(
                json.dumps(payload)
            )
            self.logger.info("End_system sent")
        except Exception as e:
            self.logger.error(f"Failed to send end_system: {e}")