import time
from ...Config import Config
from .BattleState import BattleState

HIT_DURATION = 2.0

class HitState(BattleState):
    """Boss took damage animation."""
    
    def __init__(self, service):
        super().__init__(service)
        self.start_time = 0

    def enter(self):
        print(f"[BattleState] Entering HIT")
        self.start_time = time.time()
        self.service.broadcast_state("HIT", {"battle_boss_hp": self.service.current_hp})

    def handle_monitor(self):
        if time.time() - self.start_time > HIT_DURATION:
            # Back to Fighting with new attack
            self.service.current_attack = Config.get_next_attack(self.service.current_hp)
            from .FightingState import FightingState
            self.service.change_state(FightingState(self.service))
