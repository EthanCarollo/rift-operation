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
        # Monitor for signal reset (Falling Edge) to re-arm for next hit
        if self.service.ws.last_state:
            current_confirm = self.service.ws.last_state.get("battle_hit_confirmed") is True
            if not current_confirm:
                 self.service.last_hit_confirmed = False

        if time.time() - self.start_time > HIT_DURATION:
            # Back to Fighting with new attack
            self.service.current_attack = Config.get_next_attack(self.service.current_hp)
            from .FightingState import FightingState
            self.service.change_state(FightingState(self.service))
