"""SyncManager - Handles synchronized attack triggers between two roles."""
import base64
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .RoleState import RoleState


class SyncManager:
    """
    Manages synchronized attack triggers when both players validate.
    
    The ULTRA COMBO mechanic requires:
    1. Both Dream and Nightmare to have validated the correct counter
    2. At least one valid image available for animation
    3. No previous attack_ready signal sent this phase
    """
    
    def __init__(self, roles: dict, socketio=None):
        """
        Initialize SyncManager.
        
        Args:
            roles: Dict mapping role names to RoleState instances
            socketio: SocketIO instance for emitting events
        """
        self.roles = roles
        self.socketio = socketio
        self._attack_ready = False
        self._is_attacking = False
    
    # --- LIFECYCLE ---
    
    def reset(self) -> None:
        """Reset for new attack phase."""
        self._attack_ready = False
        self._is_attacking = False
        print("[SyncManager] Reset for new phase")
    
    @property
    def is_locked(self) -> bool:
        """Check if attack has already been triggered this phase."""
        return self._attack_ready
    
    @property
    def is_attacking(self) -> bool:
        """Check if attack is currently in progress."""
        return self._is_attacking
    
    # --- DUAL VALIDATION ---
    
    def check_dual_validation(self, current_role: str, current_valid: bool) -> bool:
        """
        Check if both sides are validated for synchronized attack.
        
        Args:
            current_role: The role that just finished processing ('dream' or 'nightmare')
            current_valid: Whether the current result is a valid counter
        
        Returns:
            True if both sides are validated and attack_ready can be triggered
        """
        if self._attack_ready:
            return False
        
        current_state = self.roles.get(current_role)
        other_role = 'nightmare' if current_role == 'dream' else 'dream'
        other_state = self.roles.get(other_role)
        
        # Current role is valid if just validated OR was validated before
        is_current_valid = current_valid or (current_state.counter_validated if current_state else False)
        
        # Other role must have been validated at some point
        is_other_valid = other_state.counter_validated if other_state else False
        
        print(f"[SyncManager] 🔍 SYNC ({current_role}): cur={is_current_valid}, oth={is_other_valid}, locked={self._attack_ready}")
        
        return is_current_valid and is_other_valid
    
    def get_best_image(self, current_role: str, new_image: Optional[bytes] = None) -> Optional[bytes]:
        """
        Get the best available image for attack animation.
        
        Priority: New image > Current role cache > Other role cache
        
        Args:
            current_role: The role that just finished processing
            new_image: Newly generated image (if any)
        
        Returns:
            Best available image bytes, or None if no image available
        """
        current_state = self.roles.get(current_role)
        other_role = 'nightmare' if current_role == 'dream' else 'dream'
        other_state = self.roles.get(other_role)
        
        # Priority order
        if new_image:
            return new_image
        if current_state and current_state.last_output_image:
            return current_state.last_output_image
        if other_state and other_state.last_output_image:
            return other_state.last_output_image
        
        return None
    
    # --- ATTACK TRIGGER ---
    
    def trigger_attack_ready(self, role: str, image: bytes, label: str) -> bool:
        """
        Emit attack_ready signal to frontend.
        
        This locks the sync manager and prevents further triggers until reset.
        
        Args:
            role: Role that triggered the combo
            image: Image to animate
            label: Counter label for logging
        
        Returns:
            True if signal was emitted, False if already locked
        """
        if self._attack_ready:
            print("[SyncManager] ⚠️ Attack ready already triggered, ignoring")
            return False
        
        self._attack_ready = True
        print(f"[SyncManager] 🌟 ULTRA COMBO! Emitting attack_ready from {role}")
        
        if self.socketio and image:
            b64 = base64.b64encode(image).decode('utf-8')
            self.socketio.emit('attack_ready', {
                'role': role,
                'frame': b64,
                'label': label
            })
            print("[SyncManager] 📡 attack_ready emitted to frontend")
            return True
        
        return False
    
    def start_attack(self) -> bool:
        """
        Mark attack as in progress (prevents double execution).
        
        Returns:
            True if attack started, False if already attacking
        """
        if self._is_attacking:
            print("[SyncManager] ⚠️ Attack already in progress, ignoring duplicate")
            return False
        
        self._is_attacking = True
        return True
