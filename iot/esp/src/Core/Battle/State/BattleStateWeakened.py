"""
BattleStateWeakened.py - Boss is weakened, waiting for cage RFID
LEDs blink slowly, waiting for both agents to place cages
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateWeakened(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.WEAKENED
        self.cage_detected = False

    async def enter(self):
        self.workshop.logger.info("State WEAKENED - Boss is weakened! Place cages on RFID.")
        
        # Start slow blink animation
        if self.workshop.hardware:
            await self.workshop.hardware.blink_leds(
                BC.BattleLedColors.WEAKENED_PULSE,
                BC.BattleGameConfig.WEAKENED_BLINK_ON_MS,
                BC.BattleGameConfig.WEAKENED_BLINK_OFF_MS
            )
        
        # Notify web page
        await self.workshop.send_battle_json(
            battle_state="weakened",
            battle_hp=0,
            battle_video_play="video-battle-weakened.mp4"
        )

    async def handle_rfid(self, uid):
        """Handle cage RFID detection"""
        self.workshop.logger.info(f"RFID detected: {uid}")
        
        # Check if it's the cage UID (or accept any UID for now)
        if not self.cage_detected:
            self.cage_detected = True
            self.workshop.logger.info("Cage placed on RFID!")
            
            role = self.workshop.hardware.role
            if role == "parent":
                await self.workshop.send_battle_json(battle_cage_parent=True)
            else:
                await self.workshop.send_battle_json(battle_cage_child=True)

    async def handle_message(self, payload):
        """Check if both cages are placed"""
        parent_cage = payload.get("battle_cage_parent", False)
        child_cage = payload.get("battle_cage_child", False)
        
        if parent_cage and child_cage:
            self.workshop.logger.info("Both cages detected! Capturing boss...")
            await self.next_step()

    async def exit(self):
        if self.workshop.hardware:
            self.workshop.hardware.stop_led_effect()

    async def next_step(self):
        from src.Core.Battle.State.BattleStateCaptured import BattleStateCaptured
        await self.workshop.swap_state(BattleStateCaptured(self.workshop))
