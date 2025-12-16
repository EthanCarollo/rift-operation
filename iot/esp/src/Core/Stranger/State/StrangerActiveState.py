from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
from src.Framework.Rfid.RfidFactory import RFIDFactory
print("passed top")
from src.Core.Stranger.Rfid.StrangerRfidDelegate import StrangerRFIDDelegate
print("didnt passed bottom")
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
            cs_pin=5, 
            rst_pin=22, 
            delegate= StrangerRFIDDelegate()
        )

    def process_json_message(self, json):
        pass

    def recognize_stranger(self):
        self.controller.logger.debug("Stranger has been recognized ! Good job !")
        from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
        self.controller.swap_state(StrangerInactiveState(self.controller))


    def update(self):
        pass