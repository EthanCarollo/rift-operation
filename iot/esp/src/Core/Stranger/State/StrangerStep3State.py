from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState

class StrangerStep3State(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("step_3")

    def on_letter_detected(self, reader_name, letter):
        # Reader 3 for 'U'
        if reader_name == "Letter_3_RFID_Stranger" and letter == "U":
            self.controller.logger.debug("U detected! Moving to Step 4")
            from src.Core.Stranger.State.StrangerStep4State import StrangerStep4State
            self.controller.swap_state(StrangerStep4State(self.controller))

    def on_letter_lost(self, reader_name):
        # If 'A' is lost (Reader 2), go back to Step 2
        if reader_name == "Letter_2_RFID_Stranger":
             self.controller.logger.debug("A lost! Returning to Step 2")
             from src.Core.Stranger.State.StrangerStep2State import StrangerStep2State
             self.controller.swap_state(StrangerStep2State(self.controller))
        # If 'P' is lost, Active handle it? 
        # Actually logic is detecting transitions. If P lost, strictly we could cascade back or just jump to Active.
        elif reader_name == "Letter_1_RFID_Stranger":
             self.controller.logger.debug("P lost! Returning to Active")
             from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
             self.controller.swap_state(StrangerActiveState(self.controller))

    def update(self):
        # Check Next (3) for 'U' and Previous (1, 2) for lost
        self.controller.rfid_letter_1.check()
        self.controller.rfid_letter_2.check()
        self.controller.rfid_letter_3.check()
