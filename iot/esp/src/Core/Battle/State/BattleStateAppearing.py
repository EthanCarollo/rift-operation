"""
BattleStateAppearing.py - Boss appearing animation (5 seconds)
LEDs: White -> Role color after 5s
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateAppearing(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.APPEARING
        self._transition_task = None

    async def enter(self):
        self.workshop.logger.info("State APPEARING - Boss intro animation")
        
        # LEDs white for intro
        if self.workshop.hardware:
            self.workshop.hardware.set_led_color(BC.BattleLedColors.WHITE)
            self.workshop.hardware.set_button_led(False)
        
        # Schedule transition after 5 seconds
        self._transition_task = asyncio.create_task(self._wait_and_transition())

    async def _wait_and_transition(self):
        """Wait 5s with white LEDs, then switch to role color and start fighting"""
        try:
            await asyncio.sleep_ms(BC.BattleGameConfig.APPEARING_DURATION_MS)
            
            # Switch to role-specific color
            role_color = self.workshop.get_role_color()
            if self.workshop.hardware:
                self.workshop.hardware.set_led_color(role_color)
            
            self.workshop.logger.info(f"Role color applied: {role_color}")
            
            # Move to fighting state
            await self.next_step()
            
        except asyncio.CancelledError:
            pass

    async def exit(self):
        if self._transition_task:
            self._transition_task.cancel()

    async def next_step(self):
        from src.Core.Battle.State.BattleStateFighting import BattleStateFighting
        await self.workshop.swap_state(BattleStateFighting(self.workshop))
