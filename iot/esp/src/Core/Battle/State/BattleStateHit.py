"""
BattleStateHit.py - Boss hit animation
LEDs blink rapidly, HP decreases
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateHit(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.HIT
        self._animation_task = None

    async def enter(self):
        # Decrease HP
        self.workshop.current_hp -= 1
        self.workshop.logger.info(
            f"State HIT - Boss took damage! HP: {self.workshop.current_hp}/{BC.BattleGameConfig.TOTAL_HP}"
        )
        
        # Turn off button LED
        if self.workshop.hardware:
            self.workshop.hardware.set_button_led(False)
        
        # Notify web page
        await self.workshop.send_battle_json(
            battle_state="hit",
            battle_hp=self.workshop.current_hp,
            battle_video_play="video-battle-hit.mp4"
        )
        
        # Start blinking animation
        self._animation_task = asyncio.create_task(self._hit_animation())

    async def _hit_animation(self):
        """Blink LEDs rapidly for hit feedback"""
        try:
            if self.workshop.hardware:
                await self.workshop.hardware.blink_leds(
                    BC.BattleLedColors.HIT_FLASH,
                    BC.BattleGameConfig.HIT_BLINK_ON_MS,
                    BC.BattleGameConfig.HIT_BLINK_OFF_MS
                )
                
            # Keep blinking for 2 seconds then proceed
            await asyncio.sleep_ms(2000)
            
            # Stop blinking and restore role color
            if self.workshop.hardware:
                self.workshop.hardware.stop_led_effect()
                self.workshop.hardware.set_led_color(self.workshop.get_role_color())
            
            await self.next_step()
            
        except asyncio.CancelledError:
            pass

    async def exit(self):
        if self._animation_task:
            self._animation_task.cancel()
        if self.workshop.hardware:
            self.workshop.hardware.stop_led_effect()

    async def next_step(self):
        if self.workshop.current_hp <= 0:
            # Boss is weakened
            from src.Core.Battle.State.BattleStateWeakened import BattleStateWeakened
            await self.workshop.swap_state(BattleStateWeakened(self.workshop))
        elif self.workshop.current_round >= BC.BattleGameConfig.MAX_ROUNDS:
            # All rounds complete, boss is weakened
            from src.Core.Battle.State.BattleStateWeakened import BattleStateWeakened
            await self.workshop.swap_state(BattleStateWeakened(self.workshop))
        else:
            # Continue to next round
            from src.Core.Battle.State.BattleStateFighting import BattleStateFighting
            await self.workshop.swap_state(BattleStateFighting(self.workshop))
