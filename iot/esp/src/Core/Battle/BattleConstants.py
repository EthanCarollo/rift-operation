"""
BattleConstants.py - Shared constants for the BATTLE workshop
"""

class BattleSteps:
    """States in the battle state machine"""
    IDLE = 0          # Waiting for rift_part_count=4
    APPEARING = 1     # Boss appearing (5s intro)
    FIGHTING = 2      # Active combat round
    HIT = 3           # Boss hit animation
    WEAKENED = 4      # Boss weakened, waiting for cages
    CAPTURED = 5      # Boss captured, victory
    DONE = 6          # Workshop complete

    _NAMES = {
        IDLE: "0: IDLE",
        APPEARING: "1: APPEARING",
        FIGHTING: "2: FIGHTING",
        HIT: "3: HIT",
        WEAKENED: "4: WEAKENED",
        CAPTURED: "5: CAPTURED",
        DONE: "6: DONE"
    }

    @classmethod
    def get_name(cls, step_id):
        return cls._NAMES.get(step_id, str(step_id))


class BattleLedColors:
    """LED colors for different states and roles"""
    WHITE = (255, 255, 255)
    OFF = (0, 0, 0)
    # Role colors (after 5s intro)
    CHILD_PINK = (255, 105, 180)       # Rose vif
    PARENT_BLUE = (25, 25, 112)        # Bleu foncé (midnight blue)
    # Feedback colors
    HIT_FLASH = (255, 200, 0)          # Jaune/Orange pour feedback hit
    WEAKENED_PULSE = (128, 0, 128)     # Violet pour état affaibli
    CAPTURED_GREEN = (0, 255, 100)     # Vert pour victoire


class BattleGameConfig:
    """Game configuration"""
    # Timing (ms)
    APPEARING_DURATION_MS = 5000       # 5 seconds boss appearing
    ROLE_COLOR_TRANSITION_MS = 5000    # 5s before role color
    HIT_BLINK_ON_MS = 100
    HIT_BLINK_OFF_MS = 100
    WEAKENED_BLINK_ON_MS = 300
    WEAKENED_BLINK_OFF_MS = 300
    CAPTURED_DISPLAY_MS = 2000         # 2s victory text delay
    
    # Combat
    TOTAL_HP = 5                       # 5 HP segments
    MAX_ROUNDS = 5                     # 5 combat rounds
    
    # RFID cages
    CAGE_RFID_UID = "BD-D7-1F-21-54"   # Expected cage RFID UID
    
    # Attacks and counters (boss attack -> required counter object)
    ATTACK_COUNTERS = {
        "lightning": "shield",
        "fire": "water",
        "ice": "fire",
        "shadow": "light",
        "void": "sword"
    }
