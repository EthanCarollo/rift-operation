from .BattleState import BattleState
from .CapturedState import CapturedState

class WeakenedState(BattleState):
    """Boss is at 0 HP, waiting for capture."""

    def enter(self):
        print(f"[BattleState] Entering WEAKENED")
        self.service.current_hp = 0
        self.service.current_attack = None # Stop attacking
        self.service.broadcast_state("WEAKENED", {"battle_boss_hp": 0})

    def handle_monitor(self):
        pass
        
    def capture(self):
        self.service.change_state(CapturedState(self.service))
