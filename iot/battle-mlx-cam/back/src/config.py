"""
Configu for Battle Camera System
"""

# Key: Label defined in Training View
# Value: Prompt sent to Flux Kontext (None = skip generation)
PROMPT_MAPPING = {
    "key": "Transform this drawing into a realistic image of a golden antique key, detailed metalwork, soft shadows",
    "door": "Transform this drawing into a realistic image of a wooden medieval door, detailed wood grain, iron hinges",
    "star": "Transform this drawing into a realistic image of a glowing golden star, soft magical glow, cosmic feel",
    "eye": "Transform this drawing into a realistic image of a mystical all-seeing eye, detailed iris, ethereal glow",
    "cloud": "Transform this drawing into a realistic image of a fluffy cumulus cloud, soft lighting, atmospheric",
    "sword": "Transform this drawing into a realistic image of a steel katana sword, sharp edge, detailed hilt",
    "empty": None,      # Skip generation
    "bullshit": None,   # Skip generation - unrecognized drawing
}

# Threshold for KNN distance (lower = stricter)
KNN_DISTANCE_THRESHOLD = 13.0
# Labels that should NOT trigger 'recognised: true'
NON_RECOGNITION_LABELS = ["empty"]
# Camera Settings
CAMERA_ZOOM = 2.0       # 1.0 = No zoom, 2.0 = 2x zoom (center)
LOW_LIGHT_BOOST = True  # Enhance brightness/contrast for dark environments

# Camera Compression Settings (can be updated at runtime via web UI)
JPEG_QUALITY = 85           # 1-100, higher = better quality, larger file
CAPTURE_SCALE = 1.0         # 0.25-1.0, lower = smaller image before processing
DENOISE_STRENGTH = 0        # 0-10, higher = more denoising (slower but cleaner)

# =============================================================================
# BATTLE ATTACK SEQUENCE & COUNTER MAPPING
# =============================================================================
# Boss attacks in order (HP 5 → 1), player must draw the correct counter.
#
# Attack Sequence:
#   HP 5: DOOR    → Counter: key
#   HP 4: STAR    → Counter: door
#   HP 3: EYE     → Counter: star
#   HP 2: CLOUD   → Counter: eye
#   HP 1: KEY     → Counter: cloud (final attack)
# =============================================================================

# Attack names (French originals used by frontend/Rift server)
class Attack:
    DOOR  = "PORTE"    # HP 5
    STAR  = "ÉTOILE"   # HP 4
    EYE   = "OEIL"     # HP 3
    CLOUD = "NUAGE"    # HP 2
    KEY   = "CLÉ"      # HP 1 (final)

# Counter labels (matching KNN training labels)
class Counter:
    KEY   = "key"
    DOOR  = "door"
    STAR  = "star"
    EYE   = "eye"
    CLOUD = "cloud"

# Mapping: Boss Attack → Required Counter (KNN Label)
ATTACK_TO_COUNTER_LABEL = {
    Attack.DOOR:  Counter.KEY,    # Draw KEY to counter DOOR attack
    Attack.STAR:  Counter.DOOR,   # Draw DOOR to counter STAR attack
    Attack.EYE:   Counter.STAR,   # Draw STAR to counter EYE attack
    Attack.CLOUD: Counter.EYE,    # Draw EYE to counter CLOUD attack
    Attack.KEY:   Counter.CLOUD,  # Draw CLOUD to counter KEY attack (final)
}