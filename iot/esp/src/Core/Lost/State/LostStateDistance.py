"""
LostStateDistance.py - Distance state
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC
from src.Core.Lost.LostState import LostState

class LostStateDistance(LostState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = LC.LostSteps.DISTANCE

    async def enter(self):
        self.distance_triggered = False

    async def handle_distance(self, distance):
        if not self.distance_triggered and distance < 20:
             self.distance_triggered = True
             self.workshop.logger.info("Capteur de Distance triggered")
             self.workshop.logger.info("Futur implementation : Allumage Led Yeux Animaux")
             self.workshop.logger.info("Futur implementation : Lancement Haut-parleur Animaux")
             self.workshop.logger.info("Futur implementation : Lancement MP3 Animaux -> \"Welcome + Explication\"")
             # Auto transition to Drawing
             from src.Core.Lost.State.LostStateDrawing import LostStateDrawing
             await self.workshop.swap_state(LostStateDrawing(self.workshop))

    async def next_step(self):
        # Auto transition handled by interaction
        pass
