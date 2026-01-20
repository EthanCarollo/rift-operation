
class OperatorSteps:
    IDLE = 0
    STEP_1_READY = 1
    STEP_2_READY = 2
    STEP_3_READY = 3

    @staticmethod
    def get_name(step_id):
        if step_id == OperatorSteps.IDLE: return "IDLE"
        if step_id == OperatorSteps.STEP_1_READY: return "STEP_1_READY"
        if step_id == OperatorSteps.STEP_2_READY: return "STEP_2_READY"
        if step_id == OperatorSteps.STEP_3_READY: return "STEP_3_READY"
        return "UNKNOWN"
