
class CoordinatorSteps:
    IDLE = 0
    ACTIVE = 1    # Placeholder for main logic
    DONE = 99

    @staticmethod
    def get_name(step_id):
        if step_id == CoordinatorSteps.IDLE: return "IDLE"
        if step_id == CoordinatorSteps.ACTIVE: return "ACTIVE"
        if step_id == CoordinatorSteps.DONE: return "DONE"
        return "UNKNOWN"
