"""
LostConstants.py - Shared constants for the LOST workshop
"""

class LostSteps:
    IDLE = 0
    ACTIVE = 1
    DISTANCE = 2
    DRAWING = 3
    LIGHT = 4
    CAGE = 5
    DONE = 7

    _NAMES = {
        IDLE: "IDLE",
        ACTIVE: "ACTIVE",
        DISTANCE: "DISTANCE", 
        DRAWING: "DRAWING",
        LIGHT: "LIGHT",
        CAGE: "CAGE",
        DONE: "DONE"
    }

    @classmethod
    def get_name(cls, step_id):
        return cls._NAMES.get(step_id, str(step_id))

class LostGameConfig:
    # Auto-start trigger values (children, parent)
    TARGET_COUNTS = (2, 2)
    # Validation key
    VALID_RFID_UID = "0x93782102"
    # Timing (ms)
    DEFAULT_STEP_DELAY = 250
    START_DELAY = 100
