from src.Core.Operator.OperatorState import OperatorState
from src.Core.Operator import OperatorConstants as OC

class OperatorStateIdle(OperatorState):
    def __init__(self, workshop):
        super().__init__(workshop)
        self.step_id = OC.OperatorSteps.IDLE
