from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
import asyncio

class StrangerStep4State(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("step_4")
        self.is_finishing = False

    def on_letter_detected(self, reader_name, letter):
        # Reader 4 for 'L'
        if reader_name == "Letter_4_RFID_Stranger" and letter == "L":
            if not self.is_finishing:
                self.is_finishing = True
                self.controller.logger.debug("L detected! PAUL complete. Waiting 5s...")
                asyncio.create_task(self.finish_sequence())

    def on_letter_lost(self, reader_name):
        if self.is_finishing:
            return # Ignore loss if we are already winning

        if reader_name == "Letter_3_RFID_Stranger":
             self.controller.logger.debug("U lost! Returning to Step 3")
             from src.Core.Stranger.State.StrangerStep3State import StrangerStep3State
             self.controller.swap_state(StrangerStep3State(self.controller))
        elif reader_name == "Letter_2_RFID_Stranger":
             self.controller.logger.debug("A lost! Returning to Step 2")
             from src.Core.Stranger.State.StrangerStep2State import StrangerStep2State
             self.controller.swap_state(StrangerStep2State(self.controller))
        elif reader_name == "Letter_1_RFID_Stranger":
             self.controller.logger.debug("P lost! Returning to Active")
             from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
             self.controller.swap_state(StrangerActiveState(self.controller))

    async def finish_sequence(self):
        await asyncio.sleep(5)
        self.recognize_stranger()

    def recognize_stranger(self):
        self.controller.logger.debug("Transitions to Inactive and Open Lock")
        from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
        self.controller.swap_state(StrangerInactiveState(self.controller))
        # Open lock using servo on controller
        self.controller.servo_motor.set_angle(120)

    def update(self):
        if self.is_finishing:
            return
            
        self.controller.rfid_letter_1.check()
        self.controller.rfid_letter_2.check()
        self.controller.rfid_letter_3.check()
        self.controller.rfid_letter_4.check()
