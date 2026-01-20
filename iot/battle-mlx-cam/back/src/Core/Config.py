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

    # --- FEATURE FLAGS ---
    ENABLE_KNN = True           # Master toggle for KNN recognition

    # --- GAME DATA ---

    # Key: Label defined in Training View
    # Value: Prompt sent to Flux Kontext (None = skip generation)
    PROMPT_MAPPING = {
        "sword": "Transform this drawing into a realistic image of a medieval steel sword, sharp blade, ornate hilt, soft shadows",
        "umbrella": "Transform this drawing into a realistic image of an elegant vintage umbrella, wooden handle, fabric canopy, rain drops",
        "sun": "Transform this drawing into a realistic image of a radiant golden sun, warm rays, glowing corona, ethereal light",
        "empty": None,      # Skip generation
        "bullshit": None,   # Skip generation - unrecognized drawing
    }

    # Attack names (Boss uses these)
    class Attack:
        SHIELD = "BOUCLIER"  # HP 3 (first attack)
        RAIN   = "PLUIE"     # HP 2
        MOON   = "LUNE"      # HP 1 (final)

    # Counter labels (Player draws these)
    class Counter:
        SWORD    = "sword"
        UMBRELLA = "umbrella"
        SUN      = "sun"

    # Mapping: Boss Attack → Required Counter (KNN Label)
    # Épée > Bouclier, Parapluie > Pluie, Soleil > Lune
    ATTACK_TO_COUNTER_LABEL = {
        Attack.SHIELD: Counter.SWORD,
        Attack.RAIN:   Counter.UMBRELLA,
        Attack.MOON:   Counter.SUN,
    }

    @staticmethod
    def get_next_attack(hp: int) -> str | None:
        """Determines the next attack based on current HP (3 phases).
        
        HP >= 3 -> SHIELD (first attack)
        HP == 2 -> RAIN
        HP == 1 -> MOON (final attack)
        HP <= 0 -> None (battle over)
        """
        if hp >= 3: return Config.Attack.SHIELD
        if hp == 2: return Config.Attack.RAIN
        if hp == 1: return Config.Attack.MOON
        return None
