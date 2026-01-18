import os
from dotenv import load_dotenv

# Load .env file from up up directory relative to this file? 
# Usually best to load it at entry point, but we can ensure it here.
# Assuming standard structure back/.env
# This file is back/src/Core/Config.py
# So .env is in ../../.env
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(base_dir, '.env'))

class Config:
    """
    Static configuration class for the Battle Camera System.
    """

    # --- API KEYS ---
    @staticmethod
    def get_api_key() -> str | None:
        """Get FAL_KEY from environment."""
        return os.getenv("FAL_KEY")

    @staticmethod
    def get_replicate_key() -> str | None:
        """Get REPLICATE_URL_API from environment."""
        return os.getenv("REPLICATE_URL_API")

    @staticmethod
    def get_ws_url() -> str:
        """Get WebSocket server URL."""
        return os.getenv("WS_URL", "ws://127.0.0.1:8000/ws")

    # --- CONSTANTS ---
    
    # Threshold for KNN distance (lower = stricter)
    KNN_DISTANCE_THRESHOLD = 13.0
    
    # Labels that should NOT trigger 'recognised: true'
    NON_RECOGNITION_LABELS = ["empty"]
    
    # Camera Settings Defaults
    CAMERA_ZOOM = 2.0       # 1.0 = No zoom, 2.0 = 2x zoom (center)
    LOW_LIGHT_BOOST = True  # Enhance brightness/contrast for dark environments

    # Camera Compression Defaults
    JPEG_QUALITY = 85           # 1-100
    CAPTURE_SCALE = 1.0         # 0.25-1.0
    DENOISE_STRENGTH = 0        # 0-10

    # --- GAME DATA ---

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

    # Attack names
    class Attack:
        DOOR  = "PORTE"    # HP 5
        STAR  = "ÉTOILE"   # HP 4
        EYE   = "OEIL"     # HP 3
        CLOUD = "NUAGE"    # HP 2
        KEY   = "CLÉ"      # HP 1 (final)

    # Counter labels
    class Counter:
        KEY   = "key"
        DOOR  = "door"
        STAR  = "star"
        EYE   = "eye"
        CLOUD = "cloud"

    # Mapping: Boss Attack → Required Counter (KNN Label)
    ATTACK_TO_COUNTER_LABEL = {
        Attack.DOOR:  Counter.KEY,
        Attack.STAR:  Counter.DOOR,
        Attack.EYE:   Counter.STAR,
        Attack.CLOUD: Counter.EYE,
        Attack.KEY:   Counter.CLOUD,
    }
