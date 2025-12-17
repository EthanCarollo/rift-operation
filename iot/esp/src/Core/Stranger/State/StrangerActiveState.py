from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Stranger.Rfid.StrangerRfidDelegate import StrangerRFIDDelegate
from machine import SPI, Pin

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


        self.rfid_letter_1 = RFIDFactory.create_reader(
            spi=spi, 
            cs_pin=32, 
            rst_pin=33, 
            delegate= StrangerRFIDDelegate(),
            name= "Letter_1_RFID_Stranger"
        )
        self.rfid_letter_2 = RFIDFactory.create_reader(
            spi=spi, 
            cs_pin=16, 
            rst_pin=4, 
            delegate= StrangerRFIDDelegate(),
            name= "Letter_2_RFID_Stranger"
        )
        self.rfid_letter_3 = RFIDFactory.create_reader(
            spi=spi, 
            cs_pin=17, 
            rst_pin=21, 
            delegate= StrangerRFIDDelegate(),
            name= "Letter_3_RFID_Stranger"
        )
        self.rfid_letter_4 = RFIDFactory.create_reader(
            spi=spi, 
            cs_pin=5, 
            rst_pin=22, 
            delegate= StrangerRFIDDelegate(),
            name= "Letter_4_RFID_Stranger"
        )

    def process_json_message(self, json):
        pass

    def recognize_stranger(self):
        self.controller.logger.debug("Stranger has been recognized ! Good job !")
        from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
        self.controller.swap_state(StrangerInactiveState(self.controller))

    def give_card(self):
        pass

    def update(self):
        self.rfid_letter_1.check()
        self.rfid_letter_2.check()
        self.rfid_letter_3.check()
        self.rfid_letter_4.check()
        pass