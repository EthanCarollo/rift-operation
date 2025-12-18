import ujson as json
from src.Core.Table.PilarRfidDelegate import PilarRfidDelegate
from src.Framework.EspController import EspController
from src.Framework.Config import Config
from src.Framework.Rfid.RfidFactory import RFIDFactory
from machine import SPI, Pin

class TableController(EspController):
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger.name = "TableController"
        self.logger.info("Start to init table controller initialized")
        
        spi = SPI(
            1,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(23),
            miso=Pin(19)
        )

        self.rfid_dream_1 = RFIDFactory.create_reader(
            spi=spi, 
            cs_pin=2, 
            rst_pin=0, 
            delegate= PilarRfidDelegate(self),
            name= "Dream_1_Rfid_Lector"
        )

        self.logger.info("TableController initialized")

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            # Handle it
        except Exception as e:
            # Temporary disable that
            pass

    async def update(self):
        self.rfid_dream_1.check()
        pass