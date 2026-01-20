import time
import base64
from typing import TYPE_CHECKING

from ...Config import Config
from .BattleState import BattleState
from .HitState import HitState
from .WeakenedState import WeakenedState

if TYPE_CHECKING:
    from ..BattleService import BattleRoleState

class FightingState(BattleState):
    """Main combat loop. Handles KNN/AI."""

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
            
            # Check for attack confirmation from Rift Server (Rising Edge Detection)
            current_confirm = self.service.ws.last_state.get("battle_hit_confirmed") is True
            
            if current_confirm and not self.service.last_hit_confirmed:
                print(f"[BattleState] Attack Confirm received (Rising Edge)! Triggering HIT.")
                self.service.last_hit_confirmed = True
                self.trigger_attack()
                return
            
            # Reset latch when signal goes low
            if not current_confirm:
                self.service.last_hit_confirmed = False
            
            # Sync HP if changed passively
            if remote_hp is not None and remote_hp != self.service.current_hp:
                self.service.current_hp = remote_hp

    def on_image_task(self, role: str, state: 'BattleRoleState', image_bytes: bytes):
        """Core logic for processing images during fight."""
        try:
            print(f"[BattleService] ⚙️ Processing task for {role}...")
            
            # 1. Process via ImageProcessor
            result = self.service.processor.process_frame(image_bytes, self.service.current_attack)
            
            # 2. Update Role State
            state.knn_label = result.label
            state.knn_distance = result.distance
            state.last_label = result.label
            state.recognition_status = result.status_message
            state.prompt = result.prompt
            
            # Emit status update immediately
            self.service._emit_status()
            
            if result.should_skip:
                return

            # 3. Handle Generated Image
            if result.output_image:
                # Emit Output to Frontend
                if self.service.socketio:
                    b64 = base64.b64encode(result.output_image).decode('utf-8')
                    self.service.socketio.emit('output_frame', {
                        'role': role,
                        'frame': b64
                    })
                
                # Send to Rift Server
                b64_rift = base64.b64encode(result.output_image).decode('utf-8')
                extra = {f"battle_drawing_{role}_recognised": result.is_valid_counter}
                
                # Proxy Send
                if self.service.ws.send_image(b64_rift, role, extra):
                    print(f"[BattleService] Sent {role} to Rift Server (valid: {result.is_valid_counter})")

            # 4. Trigger Attack if Valid Counter
            if result.is_valid_counter:
                print(f"[BattleState] Valid Counter by {role}! Triggering HIT.")
                self.trigger_attack()

        except Exception as e:
            print(f"[BattleService] Error processing {role}: {e}")
            state.recognition_status = "❌ Error"


    def trigger_attack(self):
        # Decrement HP
        self.service.current_hp -= 1
        print(f"[BattleState] Attack! New HP: {self.service.current_hp}")
        
        if self.service.current_hp <= 0:
            self.service.change_state(WeakenedState(self.service))
        else:
            self.service.change_state(HitState(self.service))
