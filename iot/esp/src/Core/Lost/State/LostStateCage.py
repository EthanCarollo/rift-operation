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
        self.cage_triggered = False
        self.workshop.logger.info("State: CAGE -> Waiting for RFID Scan")

    async def handle_message(self, payload):
        if payload.get("cage_is_on_monster") is True:
             await self.next_step()
             
    async def handle_rfid(self, uid):
        # Synchronisation: Wait for Parent (Light) before accepting RFID
        if not self.workshop.light_triggered:
            self.workshop.logger.info("Wait for LOST-Parent-ESP Step3 : Light -> Finished...")
            return
        
        if self.workshop.light_triggered:
            if uid == LC.LostGameConfig.VALID_RFID_UID:
                self.workshop.logger.info("RFID VALID -> Cage Unlocked")
                self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Bravo, vous avez capturé le monstre!\"")
                self.workshop.logger.info("State: CAGE -> Sending json with value : \"cage_is_on_monster=True\"")
                await self.workshop.send_rift_json(cage=True)
                # Auto transition to Done
                await self.next_step()
            else:
                self.workshop.logger.warning(f"RFID INVALID: {uid}")
                self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Oups, pas la bonne cage! Essayez encore.\"")

    async def next_step(self):
        from src.Core.Lost.State.LostStateDone import LostStateDone
        await self.workshop.swap_state(LostStateDone(self.workshop))
