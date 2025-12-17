"""
LostStateDistance.py - Distance state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.State.LostState import LostState

class LostStateDistance(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DISTANCE

    async def enter(self):
        self.workshop.logger.info("State: DISTANCE. Waiting for button press (Simulating Drawing recog).")

    async def handle_button(self):
        self.workshop.logger.info("Button pressed -> Drawing recognized")
        self.workshop.logger.info("Futur implementation : Camera voit Dessin")
        self.workshop.logger.info("Futur implementation : Envoie Dessin (photo ou live) au llm")
        self.workshop.logger.info("Futur implementation : LLM reconnait pas dessin")
        self.workshop.logger.info("Futur implementation : Lancement Haut-parleur Animaux")
        self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Je n'ai pas compris ce que tu dessiné, il faut quelque chose pour éclairer\"")
        self.workshop.logger.info("Futur implementation : LLM reconnait dessin")
        self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Bravo je crois on va pouvoir aider ton parent avec ça\"")
        
        from src.Core.Lost.State.LostStateDrawing import LostStateDrawing
        await self.workshop.swap_state(LostStateDrawing(self.workshop))

    async def next_step(self):
        # No auto transition, blocked on button
        pass
