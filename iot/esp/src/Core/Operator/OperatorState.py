from src.Core.Operator import OperatorConstants as OC

class OperatorState:
    def __init__(self, workshop):
        self.workshop = workshop
        self.step_id = OC.OperatorSteps.IDLE

    async def enter(self):
        self.workshop.logger.info(f"Entered State: {OC.OperatorSteps.get_name(self.step_id)}")

    async def exit(self):
        pass

    async def handle_message(self, payload):
        pass

    async def handle_button(self, button_type):
        pass

    async def handle_rfid(self, uid):
        pass
