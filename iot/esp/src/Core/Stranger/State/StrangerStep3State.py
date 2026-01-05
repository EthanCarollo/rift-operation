from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState

class StrangerStep3State(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("step_3")
        self.controller.led_controller.play_from_json("data/stranger/led_anim_step3.json")

    def on_letter_detected(self, reader_name, letter):
        # Reader 3 for 'U'
        if reader_name == "Letter_3_RFID_Stranger" and letter == "U":
            self.controller.logger.debug("U detected! Moving to Step 4")
            from src.Core.Stranger.State.StrangerStep4State import StrangerStep4State
            self.controller.swap_state(StrangerStep4State(self.controller))

    def on_letter_lost(self, reader_name):
        pass

    def update(self):
        # Only check Next (3) for 'U'
        self.controller.rfid_letter_3.check()
