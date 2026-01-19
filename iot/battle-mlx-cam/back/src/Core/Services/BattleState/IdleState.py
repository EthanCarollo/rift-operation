from .BattleState import BattleState
from .AppearingState import AppearingState

START_CONDITION_PARTS = 4

class IdleState(BattleState):
    """Waiting for the game to start (Rift parts)."""
    
    def enter(self):
        print(f"[BattleState] Entering IDLE")
        self.service.broadcast_state("IDLE")

    def handle_monitor(self):
        # Check Rift for start condition
        if self.service.ws.last_state:
            parts = self.service.ws.last_state.get("rift_part_count", 0)
            if parts >= START_CONDITION_PARTS:
                print(f"[BattleState] Start Condition Met ({parts} parts)")
                self.service.change_state(AppearingState(self.service))
