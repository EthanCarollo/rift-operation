from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Stranger.Rfid.StrangerRfidDelegate import StrangerRFIDDelegate
from machine import SPI, Pin

from src.Framework.Servo.Servo import Servo
from src.Framework.Servo.ServoDelegate import ServoDelegate
import asyncio


class StrangerActiveState(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("active")
        # Ensure servo is closed/off when entering active state, if coming from inactive
        self.controller.servo_motor.off()

    def on_letter_detected(self, reader_name, letter):
        # We only care if 'P' is detected on Reader 1 (Index 0)
        # Reader 1 is "Letter_1_RFID_Stranger"
        print(reader_name)
        if reader_name == "Letter_1_RFID_Stranger" and letter == "P":
            self.controller.logger.debug("P detected! Moving to Step 2")
            from src.Core.Stranger.State.StrangerStep2State import StrangerStep2State
            self.controller.swap_state(StrangerStep2State(self.controller))

    def on_letter_lost(self, reader_name):
        pass

    def update(self):
        self.controller.rfid_letter_1.check()