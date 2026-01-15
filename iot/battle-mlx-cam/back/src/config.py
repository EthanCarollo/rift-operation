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

# Mapping: Boss Attack -> Required Counter (KNN Label)
ATTACK_TO_COUNTER_LABEL = {
    "PORTE": "key",
    "ÉTOILE": "door",
    "OEIL": "star",
    "NUAGE": "eye",
    "CLÉ": "cloud"
}