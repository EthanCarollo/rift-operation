from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Stranger.Rfid.StrangerRfidDelegate import StrangerRFIDDelegate
from machine import SPI, Pin

from src.Framework.Servo.Servo import Servo
from src.Framework.Servo.ServoDelegate import ServoDelegate


class StrangerActiveState(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)

        spi = SPI(
            1,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(23),
            miso=Pin(19)
        )

        try:
            self.rfid_letter_1 = RFIDFactory.create_reader(
                spi=spi, 
                cs_pin=2, 
                rst_pin=0, 
                delegate= StrangerRFIDDelegate(self),
                name= "Letter_1_RFID_Stranger"
            )
            self.rfid_letter_2 = RFIDFactory.create_reader(
                spi=spi, 
                cs_pin=16, 
                rst_pin=4, 
                delegate= StrangerRFIDDelegate(self),
                name= "Letter_2_RFID_Stranger"
            )
            self.rfid_letter_3 = RFIDFactory.create_reader(
                spi=spi, 
                cs_pin=17, 
                rst_pin=21, 
                delegate= StrangerRFIDDelegate(self),
                name= "Letter_3_RFID_Stranger"
            )
            self.rfid_letter_4 = RFIDFactory.create_reader(
                spi=spi, 
                cs_pin=5, 
                rst_pin=22, 
                delegate= StrangerRFIDDelegate(self),
                name= "Letter_4_RFID_Stranger"
            )
        except Exception as error:
            print(error)

        self.detected_word = [None, None, None, None]

        self.servo_motor = Servo(14, ServoDelegate())

        self.servo_motor.off()

    def on_letter_detected(self, reader_name, letter):
        index = -1
        if reader_name == "Letter_1_RFID_Stranger": index = 0
        elif reader_name == "Letter_2_RFID_Stranger": index = 1
        elif reader_name == "Letter_3_RFID_Stranger": index = 2
        elif reader_name == "Letter_4_RFID_Stranger": index = 3
        
        if index != -1:
            self.detected_word[index] = letter
            self.check_word()

    def on_letter_lost(self, reader_name):
        index = -1
        if reader_name == "Letter_1_RFID_Stranger": index = 0
        elif reader_name == "Letter_2_RFID_Stranger": index = 1
        elif reader_name == "Letter_3_RFID_Stranger": index = 2
        elif reader_name == "Letter_4_RFID_Stranger": index = 3
        
        if index != -1:
            self.detected_word[index] = None

    def check_word(self):
        word = "".join([l if l else "_" for l in self.detected_word])
        self.controller.logger.debug(f"Current word: {word}")
        if word == "PAUL":
            self.recognize_stranger()

    def process_json_message(self, json):
        pass

    def recognize_stranger(self):
        self.controller.logger.debug("Stranger has been recognized ! Good job ! Giving the rift part")
        from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
        self.controller.swap_state(StrangerInactiveState(self.controller))
        self.servo_motor.set_angle(120)

    def give_card(self):
        pass

    def update(self):
        # On check tous les lecteurs
        self.rfid_letter_1.check()
        self.rfid_letter_2.check()
        self.rfid_letter_3.check()
        self.rfid_letter_4.check()