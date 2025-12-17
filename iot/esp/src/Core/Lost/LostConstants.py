"""
LostConstants.py - Shared constants for the LOST workshop
"""

class LostSteps:
    IDLE = 0
    DISTANCE = 1
    DRAWING = 2
    LIGHT = 3
    CAGE = 4
    DONE = 5

    _NAMES = {
        IDLE: "0: IDLE",
        DISTANCE: "1: DISTANCE", 
        DRAWING: "2: DRAWING",
        LIGHT: "3: LIGHT",
        CAGE: "4: CAGE",
        DONE: "5: DONE"
    }

    @classmethod
    def get_name(cls, step_id):
        return cls._NAMES.get(step_id, str(step_id))

class LostGameConfig:
    # Auto-start trigger values (children, parent)
    TARGET_COUNTS = (2, 2)
    MAX_ATTEMPTS = 3
    # Validation key
    VALID_RFID_UID = "BD-D7-1F-21-54"
    # Timing (ms)
    DEFAULT_STEP_DELAY = 0
