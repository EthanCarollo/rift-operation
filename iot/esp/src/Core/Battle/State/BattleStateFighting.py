"""
BattleStateFighting.py - Active combat round
Waits for counter validation from Swift app, then enables button press
"""
import uasyncio as asyncio
import src.Core.Battle.BattleConstants as BC
from src.Core.Battle.BattleState import BattleState


class BattleStateFighting(BattleState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = BC.BattleSteps.FIGHTING

    async def enter(self):
        # Increment round
        self.workshop.current_round += 1
        
        # Get attack for this round
        attacks = list(BC.BattleGameConfig.ATTACK_COUNTERS.keys())
        attack_index = (self.workshop.current_round - 1) % len(attacks)
        self.workshop.current_attack = attacks[attack_index]
        
        self.workshop.logger.info(
            f"State FIGHTING - Round {self.workshop.current_round}/5 - Boss attacks with: {self.workshop.current_attack}"
        )
        
        # Reset validation state
        self.workshop.counter_valid = False
        self.workshop.button_ready = False
        
        if self.workshop.hardware:
            self.workshop.hardware.set_button_led(False)
        
        # Notify web page of new attack
        await self.workshop.send_battle_json(
            battle_state="fighting",
            battle_round=self.workshop.current_round,
            battle_attack=self.workshop.current_attack,
            battle_hp=self.workshop.current_hp
        )

    async def handle_message(self, payload):
        """Handle counter validation from Swift app"""
        role = self.workshop.hardware.role
        
        # Check for our role's counter validation
        if role == "parent":
            counter_key = "battle_counter_valid_parent"
        else:
            counter_key = "battle_counter_valid_child"
        
        if payload.get(counter_key) is True and not self.workshop.counter_valid:
            self.workshop.counter_valid = True
            self.workshop.button_ready = True
            self.workshop.logger.info("Counter validated by Swift app! Button ready.")
            
            # Light up button to indicate ready to press
            if self.workshop.hardware:
                self.workshop.hardware.set_button_led(True)
            
            # Notify server that button is ready
            if role == "parent":
                await self.workshop.send_battle_json(battle_button_ready_parent=True)
            else:
                await self.workshop.send_battle_json(battle_button_ready_child=True)
        
        # Check if BOTH players have pressed (from server broadcast)
        if payload.get("battle_hit_confirmed") is True:
            await self.next_step()

    async def handle_button(self):
        """Handle arcade button press"""
        if not self.workshop.button_ready:
            self.workshop.logger.info("Button pressed but not ready yet!")
            return
        
        self.workshop.logger.info("Button pressed at right time! Sending confirmation.")
        
        role = self.workshop.hardware.role
        if role == "parent":
            await self.workshop.send_battle_json(battle_button_pressed_parent=True)
        else:
            await self.workshop.send_battle_json(battle_button_pressed_child=True)

    async def next_step(self):
        from src.Core.Battle.State.BattleStateHit import BattleStateHit
        await self.workshop.swap_state(BattleStateHit(self.workshop))
