"""
BattleStateIdle.py - Idle state, waiting for rift_part_count=4
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateIdle(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.IDLE

    async def enter(self):
        device_id = self.workshop.controller.config.device_id
        self.workshop.logger.info(f"{device_id}: State IDLE - Waiting for rift_part_count=4")
        
        # LEDs off during idle
        if self.workshop.hardware:
            self.workshop.hardware.clear_leds()
            self.workshop.hardware.set_button_led(False)

    async def handle_message(self, payload):
        """Start battle when rift_part_count reaches 4"""
        if payload.get("rift_part_count") == 4:
            device_id = self.workshop.controller.config.device_id
            self.workshop.logger.info(f"{device_id}: Battle triggered!")
            
            # Send activation
            await self.workshop.send_battle_json(
                battle_state="appearing",
                battle_hp=self.workshop.current_hp,
                battle_video_play="video-battle-appearing.mp4"
            )
            await self.next_step()

    async def next_step(self):
        from src.Core.Battle.State.BattleStateAppearing import BattleStateAppearing
        await self.workshop.swap_state(BattleStateAppearing(self.workshop))
