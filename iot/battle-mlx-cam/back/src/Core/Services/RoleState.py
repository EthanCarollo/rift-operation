"""RoleState - Clean encapsulated state for a player role (Dream/Nightmare)."""
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class RoleState:
    """
    Manages state for one player role in the battle.
    
    Each role (Dream/Nightmare) has its own instance tracking:
    - KNN recognition results
    - Image generation state
    - Validation flags for synchronized attacks
    - Image processing settings (crop, rotation, grayscale)
    """
    
    role: str
    
    # Processing timing
    last_gen_time: float = 0
    processing: bool = False
    
    # KNN Recognition
    knn_label: Optional[str] = None
    knn_distance: Optional[float] = None
    last_label: Optional[str] = None
    recognition_status: str = "Waiting..."
    prompt: Optional[str] = None
    
    # Generated image cache
    last_output_image: Optional[bytes] = None
    
    # Validation flags (per attack phase)
    counter_validated: bool = False
    valid_image_generated: bool = False
    
    # Image processing settings
    crop: Optional[dict] = None
    rotation: int = 0
    grayscale: bool = False
    
    # --- LIFECYCLE METHODS ---
    
    def reset_for_new_phase(self) -> None:
        """Reset flags when entering a new attack phase (FIGHTING)."""
        self.counter_validated = False
        self.last_output_image = None
        self.valid_image_generated = False
        print(f"[RoleState] {self.role} reset for new phase")
    
    def reset_all(self) -> None:
        """Full reset for new battle."""
        self.last_gen_time = 0
        self.processing = False
        self.knn_label = None
        self.knn_distance = None
        self.last_label = None
        self.recognition_status = "Waiting..."
        self.prompt = None
        self.last_output_image = None
        self.counter_validated = False
        self.valid_image_generated = False
    
    # --- STATE UPDATES ---
    
    def update_knn_result(self, label: str, distance: float, status: str) -> None:
        """Update KNN recognition results."""
        self.knn_label = label
        self.knn_distance = distance
        self.last_label = label
        self.recognition_status = status
    
    def mark_counter_validated(self) -> None:
        """Mark that this role has validated the correct counter."""
        if not self.counter_validated:
            self.counter_validated = True
            print(f"[RoleState] ✓ {self.role} counter validated")
    
    def mark_image_generated(self) -> None:
        """Mark that a valid image has been generated - prevents regeneration."""
        if not self.valid_image_generated:
            self.valid_image_generated = True
            print(f"[RoleState] ✅ {self.role} locked - valid image generated")
    
    def cache_output_image(self, image: bytes) -> None:
        """Cache the generated output image."""
        self.last_output_image = image
    
    # --- PREDICATES ---
    
    @property
    def can_generate(self) -> bool:
        """Check if this role can start a new image generation."""
        return not self.valid_image_generated and not self.processing
    
    @property
    def has_valid_counter(self) -> bool:
        """Check if this role has validated the correct counter at some point."""
        return self.counter_validated
    
    @property
    def has_cached_image(self) -> bool:
        """Check if there's a cached output image available."""
        return self.last_output_image is not None
    
    # --- RATE LIMITING ---
    
    def can_process(self, rate_limit_seconds: float) -> bool:
        """Check if enough time has passed since last generation."""
        return time.time() - self.last_gen_time >= rate_limit_seconds
    
    def start_processing(self) -> None:
        """Mark processing as started and update timestamp."""
        self.processing = True
        self.last_gen_time = time.time()
    
    def finish_processing(self) -> None:
        """Mark processing as finished."""
        self.processing = False
    
    # --- SERIALIZATION ---
    
    def to_status_dict(self) -> dict:
        """Return status data for frontend display."""
        return {
            'role': self.role,
            'knn_label': self.knn_label,
            'knn_distance': self.knn_distance,
            'recognition_status': self.recognition_status,
            'counter_validated': self.counter_validated,
            'has_image': self.has_cached_image,
        }
