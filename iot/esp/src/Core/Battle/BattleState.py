"""
BattleState.py - Base class for BATTLE workshop states
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC

class BattleState:
    def __init__(self, workshop):
        self.workshop = workshop
        self.step_id = None

    async def enter(self):
        """Called when entering the state"""
        pass

    async def exit(self):
        """Called when exiting the state"""
        pass

    async def handle_message(self, payload):
        """Handle WebSocket message payload"""
        pass

    async def handle_rfid(self, uid):
        """Handle RFID tag read"""
        pass

    async def handle_button(self):
        """Handle button press"""
        pass

    async def next_step(self):
        """Transition to the next state"""
        pass

    async def fast_forward_to(self, target_step):
        """Fast forward to a specific step"""
        if self.step_id >= target_step:
            return

        self.workshop.controller.logger.info(
            "FAST FORWARD -> {}".format(BC.BattleSteps.get_name(target_step))
        )
        
        if target_step == BC.BattleSteps.DONE:
            from src.Core.Battle.State.BattleStateDone import BattleStateDone
            await self.workshop.swap_state(BattleStateDone(self.workshop))
