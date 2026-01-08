"""
BattleStateCaptured.py - Boss captured! Victory animation
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateCaptured(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.CAPTURED
        self._victory_task = None

    async def enter(self):
        self.workshop.logger.info("State CAPTURED - Boss captured! Victory!")
        
        # Solid green for victory
        if self.workshop.hardware:
            self.workshop.hardware.set_led_color(BC.BattleLedColors.CAPTURED_GREEN)
        
        # Notify web page
        await self.workshop.send_battle_json(
            battle_state="captured",
            battle_video_play="video-battle-captured.mp4"
        )
        
        # Wait then transition to done
        self._victory_task = asyncio.create_task(self._victory_sequence())

    async def _victory_sequence(self):
        """Victory display sequence"""
        try:
            # Show "Étranger vaincu" for 5 seconds
            await asyncio.sleep_ms(5000)
            
            # Then add the final message and proceed
            await self.workshop.send_battle_json(battle_state="done")
            await self.next_step()
            
        except asyncio.CancelledError:
            pass

    async def exit(self):
        if self._victory_task:
            self._victory_task.cancel()

    async def next_step(self):
        from src.Core.Battle.State.BattleStateDone import BattleStateDone
        await self.workshop.swap_state(BattleStateDone(self.workshop))
