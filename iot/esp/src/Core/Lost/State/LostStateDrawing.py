"""
LostStateDrawing.py - Drawing state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateDrawing(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DRAWING

    async def enter(self):
        self.drawing_triggered = False
        self.workshop.logger.info("State: DRAWING -> Waiting for button press (Simulating Drawing recognition)")

    async def handle_button(self):
        if not self.drawing_triggered:
            self.drawing_triggered = True
            self.workshop.logger.info("Button pressed -> Drawing recognized")
            self.workshop.logger.info("Futur implementation : Camera voit Dessin")
            self.workshop.logger.info("Futur implementation : Envoie Dessin (photo ou live) au llm")
            self.workshop.logger.info("Futur implementation : LLM reconnait pas dessin")
            self.workshop.logger.info("Futur implementation : Lancement Haut-parleur Animaux")
            self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Je n'ai pas compris ce que tu dessiné, il faut quelque chose pour éclairer\"")
            self.workshop.logger.info("Futur implementation : LLM reconnait dessin")
            self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Bravo je crois on va pouvoir aider ton parent avec ça\"")

        self.workshop.logger.info("State: DRAWING -> Sending json with value : \"torch_scanned=True\"")
        await self.workshop.send_rift_json(torch=True)
        # Auto transition to Light
        await self.next_step()

    async def next_step(self):
        from src.Core.Lost.State.LostStateLight import LostStateLight
        await self.workshop.swap_state(LostStateLight(self.workshop))