import time
from .BattleState import BattleState

INITIAL_HP = 3  # 3-phase combat: BOUCLIER → PLUIE → LUNE
APPEARING_DURATION = 10.0

class AppearingState(BattleState):
    """Boss appearing intro sequence."""
    
    def __init__(self, service):
        super().__init__(service)
        self.start_time = 0

    def enter(self):
        print(f"[BattleState] Entering APPEARING")
        self.start_time = time.time()
        # Reset Game Variables
        self.service.current_hp = INITIAL_HP
        self.service.current_attack = None
        self.service.broadcast_state("APPEARING", {"battle_boss_hp": INITIAL_HP})

    def handle_monitor(self):
        # Wait for animation duration
        if time.time() - self.start_time > APPEARING_DURATION:
            from .FightingState import FightingState
            self.service.change_state(FightingState(self.service))
