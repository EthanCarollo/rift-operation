"""
Configu for Battle Camera System
"""

# Key: Label defined in Training View
# Value: Prompt sent to Flux Kontext
PROMPT_MAPPING = {
    "key": "A golden key illustration, vector art sticker style, white background, isolated, high contrast",
    "door": "A wooden door illustration, vector art sticker style, white background, isolated, high contrast",
    "star": "A cute yellow star illustration, vector art sticker style, white background, isolated, high contrast",
    "eye": "A mystic eye illustration, vector art sticker style, white background, isolated, high contrast",
    "cloud": "A fluffy blue cloud illustration, vector art sticker style, white background, isolated, high contrast",
    "sword": "A sharp steel katana sword, vector art sticker style, white background, isolated, high contrast",
    "empty": "pure white background",
    "bullshit": "random cartoon scribble, white background",
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