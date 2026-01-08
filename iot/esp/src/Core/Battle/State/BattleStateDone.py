"""
BattleStateDone.py - Workshop complete, LEDs off
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateDone(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.DONE

    async def enter(self):
        self.workshop.logger.info("State DONE - Battle workshop complete")
        
        # Turn off all LEDs
        if self.workshop.hardware:
            self.workshop.hardware.clear_leds()
            self.workshop.hardware.set_button_led(False)

    async def handle_message(self, payload):
        """Handle reset command"""
        if payload.get("reset_system") is True:
            await self.workshop.reset()
