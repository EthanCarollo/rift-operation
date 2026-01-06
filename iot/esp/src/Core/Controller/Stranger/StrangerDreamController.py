from src.Framework.Config.Config import Config
from src.Framework.EspController import EspController
from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Stranger.Rfid.StrangerRfidDelegate import StrangerRFIDDelegate
from src.Framework.Servo.Servo import Servo
from src.Framework.Servo.ServoDelegate import ServoDelegate
from machine import SPI, Pin
import ujson as json

class StrangerDreamController(EspController):
    def __init__(self, config: Config):
        super().__init__(config, "StrangerDreamController")

        spi = SPI(
            1,
            baudrate=5_000_000,
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
            # Handle error appropriately (maybe log it)
            # self.logger.error(f"RFID Init failed: {error}")

        self.servo_motor = Servo(14, ServoDelegate())
        self.servo_motor.off()
        
        self.current_reader_index = 0

        self.swap_state(StrangerInactiveState(self))

    def swap_state(self, state):
        self.logger.debug(f"Swapping to StrangerController to new state : {state.__class__.__name__}")
        self.state = state

    async def process_message(self, message):
        try:
            data = json.loads(message)
            # self.logger.info(f"Received message: {data}")
            self.state.process_json_message(json= data)
        except Exception as e:
            # Temporary disable that
            pass

    async def update(self):
        if self.state:
            self.state.update()

    def on_letter_detected(self, reader_name, letter):
        if hasattr(self.state, 'on_letter_detected'):
            self.state.on_letter_detected(reader_name, letter)

    def on_letter_lost(self, reader_name):
         if hasattr(self.state, 'on_letter_lost'):
            self.state.on_letter_lost(reader_name)