
class OperatorSteps:
    IDLE = 0
    RIFT_CLOSING = 1
    BATTLE_MODE = 2
    VICTORY = 3

    @staticmethod
    def get_name(step_id):
        if step_id == OperatorSteps.IDLE: return "IDLE"
        if step_id == OperatorSteps.RIFT_CLOSING: return "RIFT_CLOSING"
        if step_id == OperatorSteps.BATTLE_MODE: return "BATTLE_MODE"
        if step_id == OperatorSteps.VICTORY: return "VICTORY"
        return "UNKNOWN"

class OperatorConfig:
    CAGE_UUID = "04050607" # Replace with actual UUID
