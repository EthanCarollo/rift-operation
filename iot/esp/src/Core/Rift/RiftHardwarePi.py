import spidev
import RPi.GPIO as GPIO
from src.Framework.Rfid.RfidReaderPi import RfidReaderPi
from src.Core.Rift.RiftRfidDelegate import RiftRfidDelegate

class RiftHardwarePi:
    def __init__(self, controller):
        self.logger = controller.logger
        self.controller = controller
        self.workshop = None

        self.spi = None
        self.readers = []
        self.delegate = RiftRfidDelegate(None)
        
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.init_hardware()

    def attach_workshop(self, workshop):
        self.workshop = workshop
        self.delegate.workshop = workshop

    def init_hardware(self):
        self.logger.info("Initializing RIFT Hardware (Raspberry Pi)")
        
        # Initialize SPI
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0) # Bus 0, Device 0
            self.spi.max_speed_hz = 1000000 
            self.logger.info("SPI initialized (spidev 0.0)")
        except Exception as e:
            self.logger.error(f"SPI init failed: {e}")
            return

        # Readers Configuration (BCM Pins)
        # Dream 1: CS=8 (CE0), RST=25
        # Dream 2: CS=7 (CE1), RST=24
        # Dream 3: CS=22, RST=27
        configs = [
            {"name": "DreamSlot1",     "cs": 4,   "rst": 27},
            {"name": "DreamSlot2",     "cs": 17,  "rst": 27},
            {"name": "DreamSlot3",     "cs": 16,  "rst": 27},
            {"name": "NightmareSlot1", "cs": 5,   "rst": 27},
            {"name": "NightmareSlot2", "cs": 13,  "rst": 27},
            {"name": "NightmareSlot3", "cs": 14,  "rst": 27},
        ]
        
        self.readers = []
        for cfg in configs:
            try:
                reader = RfidReaderPi(
                    self.spi, 
                    cfg["cs"], 
                    cfg["rst"], 
                    self.delegate, 
                    name=cfg["name"]
                )
                self.readers.append(reader)
            except Exception as e:
                self.logger.error(f"Failed to init {cfg['name']}: {e}")

        self.logger.info(f"Initialized {len(self.readers)} RFID readers")

    def update(self):
        for reader in self.readers:
            try:
                reader.check()
            except Exception as e:
                self.logger.error(f"RFID error on {reader.name}: {e}")
    
    def cleanup(self):
        self.spi.close()
        GPIO.cleanup()
