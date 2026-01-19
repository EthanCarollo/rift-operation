from ...Config import Config
from .BattleState import BattleState
from .HitState import HitState
from .WeakenedState import WeakenedState

class FightingState(BattleState):
    """Main combat loop."""

    def enter(self):
        print(f"[BattleState] Entering FIGHTING")
        if not self.service.current_attack:
             self.service.current_attack = Config.get_next_attack(self.service.current_hp)
        
        self.service.broadcast_state("FIGHTING", {
            "battle_boss_attack": self.service.current_attack,
            "battle_boss_hp": self.service.current_hp
        })

    def handle_monitor(self):
        # Sync with Rift State (Game Master Authority)
        if self.service.ws.last_state:
            remote_state = self.service.ws.last_state.get("battle_state")
            remote_hp = self.service.ws.last_state.get("battle_boss_hp", self.service.current_hp)
            
            # If Server says HIT, we follow
            if remote_state == "HIT":
                print(f"[BattleState] Remote HIT detected! Syncing...")
                self.service.current_hp = remote_hp
                self.service.change_state(HitState(self.service))
                return
                
            elif remote_state == "WEAKENED":
                self.service.current_hp = 0
                self.service.change_state(WeakenedState(self.service))
                return
            
            # Sync HP if changed passively
            if remote_hp is not None and remote_hp != self.service.current_hp:
                self.service.current_hp = remote_hp

    def process_frame(self, role: str, image_bytes: bytes):
        result = super().process_frame(role, image_bytes)
        if result and result.is_valid_counter:
            print(f"[BattleState] Valid Counter by {role}! Triggering HIT.")
            self.trigger_attack()
        return result

    def trigger_attack(self):
        # Decrement HP
        self.service.current_hp -= 1
        print(f"[BattleState] Attack! New HP: {self.service.current_hp}")
        
        if self.service.current_hp <= 0:
            self.service.change_state(WeakenedState(self.service))
        else:
            self.service.change_state(HitState(self.service))
