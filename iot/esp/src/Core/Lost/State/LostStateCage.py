"""
LostStateCage.py - Cage state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateCage(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.CAGE

    async def enter(self):
        self.workshop.logger.info("State: CAGE. Waiting for RFID Tag...")

    async def handle_signal(self, signal):
        if signal == "light_sensor_triggered":
            self.workshop.logger.info("Wait for LOST-Parent-ESP Step3 : Light -> Finished...")
            self.workshop.logger.info(f"-------- {LC.LostSteps.get_name(LC.LostSteps.LIGHT)} -> {LC.LostSteps.get_name(LC.LostSteps.CAGE)} --------")

    async def handle_rfid(self, uid):
        # Synchronisation: Wait for Parent (Light) before accepting RFID
        if not self.workshop.light_triggered:
            self.workshop.logger.info("Wait for LOST-Parent-ESP Step3 : Light -> Finished...")
            return

        if uid == LC.LostGameConfig.VALID_RFID_UID:
             self.workshop.logger.info("RFID VALID -> Cage Unlocked")
             await self.workshop.send_rift_json(cage=True)
             from src.Core.Lost.State.LostStateDone import LostStateDone
             await self.workshop.swap_state(LostStateDone(self.workshop))
        else:
             self.workshop.logger.warning(f"RFID INVALID: {uid}. Expected: {LC.LostGameConfig.VALID_RFID_UID}")
             # Optional: Feedback?

    async def next_step(self):
        pass
