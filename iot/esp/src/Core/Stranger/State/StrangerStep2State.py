from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState

class StrangerStep2State(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("step_2")
        # Optional: Different LED animation if available
        # self.controller.led_controller.play_from_json("data/stranger/led_anim_step2.json")

    def on_letter_detected(self, reader_name, letter):
        # Reader 2 for 'A'
        if reader_name == "Letter_2_RFID_Stranger" and letter == "A":
            self.controller.logger.debug("A detected! Moving to Step 3")
            from src.Core.Stranger.State.StrangerStep3State import StrangerStep3State
            self.controller.swap_state(StrangerStep3State(self.controller))
            
    def on_letter_lost(self, reader_name):
        # If 'P' is lost (Reader 1), go back to Active?
        if reader_name == "Letter_1_RFID_Stranger":
             self.controller.logger.debug("P lost! Returning to Active")
             from src.Core.Stranger.State.StrangerActiveState import StrangerActiveState
             self.controller.swap_state(StrangerActiveState(self.controller))

    def update(self):
        # Check Next (2) for 'A' and Previous (1) for lost 'P'
        self.controller.rfid_letter_1.check()
        self.controller.rfid_letter_2.check()
