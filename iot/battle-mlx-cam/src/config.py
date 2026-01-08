"""
Configu for Battle Camera System
"""

# Key: Label defined in Training View
# Value: Prompt sent to Flux Kontext
PROMPT_MAPPING = {
    "key": "A key door in cartoon style, white background",
    "door": "A door in cartoon style, white background",
    "star": "A star with eyes in cartoon style, white background",
    "eye": "An eye in cartoon style, white background",
    "cloud": "A fluffy white cloud in cartoon style, white background",
    "empty": "The empty white background",
    "bullshit": "A pile of cartoon style garbage, white background",
}

# Threshold for KNN distance (lower = stricter)
KNN_DISTANCE_THRESHOLD = 10.0
# Labels that should NOT trigger 'recognised: true'
NON_RECOGNITION_LABELS = ["empty"]
# Camera Settings
CAMERA_ZOOM = 2.0       # 1.0 = No zoom, 2.0 = 2x zoom (center)
LOW_LIGHT_BOOST = False  # Enhance brightness/contrast for dark environments