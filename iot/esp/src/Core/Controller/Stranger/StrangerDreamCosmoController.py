from src.Framework.Config.Config import Config
from src.Framework.EspController import EspController
from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Stranger.Rfid.CosmoRfidDelegate import CosmoRFIDDelegate
from src.Framework.Servo.Servo import Servo
from src.Framework.Servo.ServoDelegate import ServoDelegate
from machine import SPI, Pin
from src.Framework.Json.RiftOperationJsonData import RiftOperationJsonData
import ujson as json

class StrangerDreamCosmoController(EspController):
    def __init__(self, config: Config):
        super().__init__(config, "StrangerDreamCosmoController")

        # Detection mode: inactive by default, activated on step_4
        self.detection_mode = False

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
            self.rfid_dark_cosmo = RFIDFactory.create_reader(
                spi=spi, 
                cs_pin=2, 
                rst_pin=4, 
                delegate= CosmoRFIDDelegate(self),
                name= "Dark_Cosmo_RFID_Stranger"
            )
        except Exception as error:
            print(error)
            # Handle error appropriately (maybe log it)
            # self.logger.error(f"RFID Init failed: {error}")

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            
            # Check for step_4 to enable detection mode
            if "stranger_state" in data and data["stranger_state"] == "step_4":
                self.detection_mode = True
                self.logger.info("Detection mode activated (step_4)")
        except Exception as e:
            pass

    async def update(self):
        # Only check RFID when in detection mode
        if self.detection_mode:
            self.rfid_dark_cosmo.check()

    def on_dark_cosmo_detected(self):
        # Only process if in detection mode
        if not self.detection_mode:
            print("Detected dark cosmo, but shouldn't detect it now.")
            return
            
        msg_json = RiftOperationJsonData(
            device_id=self.logger_name,
            is_dark_cosmo_here=True
        ).to_json()

        self.websocket_client.send_now(msg_json)
        print("Dark cosmo detected...")
        
        # Switch back to inactive mode after detection
        self.detection_mode = False
        self.logger.info("Detection mode deactivated (dark cosmo detected)")

    def on_dark_cosmo_lost(self):
        # Do nothing on lost
        pass