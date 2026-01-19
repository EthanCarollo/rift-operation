import time
from .BattleState import BattleState

# Circular import prevention usually handled by imports inside methods or if TYPE_CHECKING
# But here we need FightingState class for transition.
# We will import it inside handle_monitor to avoid circular dependency at module level if needed,
# or just rely on Python handling it if structure allows.
# For simplicity, let's use local import if safe.

INITIAL_HP = 5
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
        self.service.current_attack = None # Will set first attack in Fighting
        self.service.broadcast_state("APPEARING", {"battle_boss_hp": INITIAL_HP})

    def handle_monitor(self):
        # Wait for animation duration
        if time.time() - self.start_time > APPEARING_DURATION:
            from .FightingState import FightingState
            self.service.change_state(FightingState(self.service))
