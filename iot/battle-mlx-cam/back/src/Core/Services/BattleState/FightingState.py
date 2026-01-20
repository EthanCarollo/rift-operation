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
        self.attack_ready = False # Lock flag for synchronized attack
        
        if not self.service.current_attack:
             self.service.current_attack = Config.get_next_attack(self.service.current_hp)
        
        self.service.broadcast_state("FIGHTING", {
            "battle_boss_attack": self.service.current_attack,
            "battle_boss_hp": self.service.current_hp
        })

    def handle_monitor(self):
        # ... (unchanged) ...
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
        # STOP if already ready to attack (prevent new inferences)
        if hasattr(self, 'attack_ready') and self.attack_ready:
            return

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

            # 3. Handle Generated Image (and check for Dual-Side Success)
            if result.output_image:
                # Save to state cache
                state.last_output_image = result.output_image
                
                # Emit Output to Frontend (Preview)
                if self.service.socketio:
                    b64 = base64.b64encode(result.output_image).decode('utf-8')
                    self.service.socketio.emit('output_frame', {
                        'role': role,
                        'frame': b64
                    })
                
                # Send to Rift Server (Legacy/Proxy)
                b64_rift = base64.b64encode(result.output_image).decode('utf-8')
                extra = {f"battle_drawing_{role}_recognised": result.is_valid_counter}
                if self.service.ws.send_image(b64_rift, role, extra):
                    print(f"[BattleService] Sent {role} to Rift Server")

            # --- SYNCHRONIZED ATTACK CHECK ---
            # Check Dual Validation (Both sides must be valid)
            current_valid = result.is_valid_counter
            
            # Check other role
            other_role = 'nightmare' if role == 'dream' else 'dream'
            other_state = self.service.roles.get(other_role)
            required = Config.ATTACK_TO_COUNTER_LABEL.get(self.service.current_attack)
            
            other_valid = False
            other_label = other_state.last_label if other_state else None
            if other_state and other_state.last_label == required:
                other_valid = True
            
            # Debug: Log sync check status
            print(f"[BattleState] 🔍 SYNC ({role}): cur={current_valid}, oth={other_valid} (label={other_label}, need={required}), locked={getattr(self, 'attack_ready', False)}")
            
            # SYNCHRONIZED SUCCESS: Current Valid + Other Valid + Image Available
            # CRITICAL: Check attack_ready flag to prevent race condition (both roles might reach here)
            if current_valid and other_valid and not getattr(self, 'attack_ready', False):
                 # We need an image for the animation. usage priority: Current New -> Current Cached -> Other Cached
                 final_image = result.output_image or state.last_output_image or (other_state.last_output_image if other_state else None)
                 
                 if final_image:
                     print(f"[BattleState] 🌟 ULTRA COMBO! Both sides valid & Image Ready. Locking inference.")
                     self.attack_ready = True
                     
                     # Emit SIGNAL to Frontend to start Animation
                     if self.service.socketio:
                         b64_final = base64.b64encode(final_image).decode('utf-8')
                         self.service.socketio.emit('attack_ready', {
                             'role': role,
                             'frame': b64_final,
                             'label': result.label
                         })
                 else:
                     print(f"[BattleState] Both valid but NO IMAGE ready yet. Waiting...")

            # 4. Standard validation notification (non-locking)
            if result.is_valid_counter:

                if self.service.socketio:
                    self.service.socketio.emit('counter_validated', {
                        'role': role,
                        'label': result.label,
                        'attack': self.service.current_attack
                    })


        except Exception as e:
            print(f"[BattleService] Error processing {role}: {e}")
            state.recognition_status = "❌ Error"


    def trigger_attack(self):
        if getattr(self, 'is_attacking', False):
             print(f"[BattleState] ⚠️ Attack already in progress. Ignoring duplicate trigger.")
             return
        
        self.is_attacking = True
        
        # Decrement HP
        old_hp = self.service.current_hp
        self.service.current_hp -= 1
        new_hp = self.service.current_hp
        print(f"[BattleState] ⚔️ Attack! HP: {old_hp} → {new_hp}")
        
        if self.service.current_hp <= 0:
            print(f"[BattleState] 🏆 HP reached 0! Transitioning to WEAKENED")
            self.service.change_state(WeakenedState(self.service))
        else:
            next_attack = Config.get_next_attack(new_hp)
            print(f"[BattleState] 🔄 Transitioning to HIT, next attack will be: {next_attack}")
            self.service.change_state(HitState(self.service))

