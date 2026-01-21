import time
import base64
from typing import TYPE_CHECKING

from ...Config import Config
from .BattleState import BattleState
from .HitState import HitState
from .WeakenedState import WeakenedState

if TYPE_CHECKING:
    from ..RoleState import RoleState

class FightingState(BattleState):
    """Main combat loop. Handles KNN recognition and AI image generation."""

    def enter(self):
        print("[FightingState] Entering FIGHTING")
        
        # Reset sync manager for new phase
        if self.service.sync_manager:
            self.service.sync_manager.reset()
        
        # Reset all role states for new attack phase
        for role_state in self.service.roles.values():
            role_state.reset_for_new_phase()
        
        # Determine attack if not set
        if not self.service.current_attack:
            self.service.current_attack = Config.get_next_attack(self.service.current_hp)
        
        print(f"[FightingState] Attack: {self.service.current_attack}, HP: {self.service.current_hp}")
        
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

    def on_image_task(self, role: str, state: 'RoleState', image_bytes: bytes):
        """
        Core image processing logic during fight.
        
        Flow:
        1. Check if we can process (not locked, not already generated)
        2. Process image through ImageProcessor
        3. Update state with results
        4. If valid counter, mark validated and check for ULTRA COMBO
        5. If both sides validated, trigger attack_ready signal
        """
        sync = self.service.sync_manager
        
        # Guard: Stop if attack already triggered or can't generate
        if sync and sync.is_locked:
            return
        if not state.can_generate:
            return

        try:
            print(f"[FightingState] ⚙️ Processing {role}...")
            
            # 1. Process image via ImageProcessor
            result = self.service.processor.process_frame(image_bytes, self.service.current_attack)
            
            # 2. Update role state with KNN results
            state.update_knn_result(result.label, result.distance, result.status_message)
            state.prompt = result.prompt
            self.service._emit_status()
            
            if result.should_skip:
                return

            # 3. Handle generated image
            if result.output_image:
                state.cache_output_image(result.output_image)
                
                if result.is_valid_counter:
                    state.mark_counter_validated()
                    state.mark_image_generated()
                
                # Emit preview to frontend
                self._emit_output_frame(role, result.output_image)
                
                # Send to Rift Server
                self._send_to_rift(role, result.output_image, result.is_valid_counter)

            # 4. Check for ULTRA COMBO (dual-side validation)
            if result.is_valid_counter:
                state.mark_counter_validated()
                self._emit_counter_validated(role, result.label)
            
            if sync and sync.check_dual_validation(role, result.is_valid_counter):
                final_image = sync.get_best_image(role, result.output_image)
                if final_image:
                    sync.trigger_attack_ready(role, final_image, result.label)

        except Exception as e:
            print(f"[FightingState] Error processing {role}: {e}")
            state.recognition_status = "❌ Error"

    # --- HELPER METHODS ---
    
    def _emit_output_frame(self, role: str, image: bytes):
        """Emit generated image preview to frontend."""
        if self.service.socketio:
            b64 = base64.b64encode(image).decode('utf-8')
            self.service.socketio.emit('output_frame', {'role': role, 'frame': b64})
    
    def _send_to_rift(self, role: str, image: bytes, is_valid: bool):
        """Send image to Rift Server."""
        b64 = base64.b64encode(image).decode('utf-8')
        extra = {f"battle_drawing_{role}_recognised": is_valid}
        if self.service.ws.send_image(b64, role, extra):
            print(f"[FightingState] Sent {role} to Rift Server")
    
    def _emit_counter_validated(self, role: str, label: str):
        """Emit counter validation notification."""
        if self.service.socketio:
            self.service.socketio.emit('counter_validated', {
                'role': role,
                'label': label,
                'attack': self.service.current_attack
            })

    def trigger_attack(self):
        """Execute attack - decrement HP and transition state."""
        sync = self.service.sync_manager
        
        # Guard: Prevent double execution
        if sync and not sync.start_attack():
            return
        
        # Decrement HP
        old_hp = self.service.current_hp
        self.service.current_hp -= 1
        new_hp = self.service.current_hp
        print(f"[FightingState] ⚔️ Attack! HP: {old_hp} → {new_hp}")
        
        # Transition based on remaining HP
        if new_hp <= 0:
            print("[FightingState] 🏆 HP reached 0! → WEAKENED")
            self.service.change_state(WeakenedState(self.service))
        else:
            next_attack = Config.get_next_attack(new_hp)
            print(f"[FightingState] 🔄 → HIT (next: {next_attack})")
            self.service.change_state(HitState(self.service))
