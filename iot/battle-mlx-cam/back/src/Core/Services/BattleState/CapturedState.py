from .BattleState import BattleState

class CapturedState(BattleState):
    """Victory state."""

    def enter(self):
        print(f"[BattleState] Entering CAPTURED")
        self.service.broadcast_state("CAPTURED")

    def handle_monitor(self):
        pass
