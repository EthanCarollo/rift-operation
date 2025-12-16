"""
LostConstants - Shared constants for the LOST workshop
"""

# State machine steps
STEP_IDLE = 0
STEP_ACTIVE = 1
STEP_DISTANCE = 2
STEP_DRAWING = 3
STEP_LIGHT = 4
STEP_CAGE = 5
STEP_DONE = 7
# Step names for logging
STEP_NAMES = {
    STEP_IDLE: "IDLE",
    STEP_ACTIVE: "ACTIVE",
    STEP_DISTANCE: "DISTANCE", 
    STEP_DRAWING: "DRAWING",
    STEP_LIGHT: "LIGHT",
    STEP_CAGE: "CAGE",
    STEP_DONE: "DONE"
}

# Auto-start trigger values (children, parent)
TARGET_COUNTS = (2, 2)

# Timing constants (ms)
DEFAULT_STEP_DELAY = 250
START_DELAY = 100
