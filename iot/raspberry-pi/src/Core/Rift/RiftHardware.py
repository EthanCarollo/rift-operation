import spidev
import RPi.GPIO as GPIO
import time
from src.Framework.Rfid.RfidReader import RfidReader
from src.Core.Rift.RiftRfidDelegate import RiftRfidDelegate

class RiftHardware:
    def __init__(self, controller):
        self.logger = controller.logger
        self.controller = controller
        self.workshop = None

        self.spi = None

        self.delegate = RiftRfidDelegate(None)
        
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.init_hardware()

    def attach_workshop(self, workshop):
        self.workshop = workshop
        self.delegate.workshop = workshop

    def init_hardware(self):
        self.logger.info("Initializing RIFT Hardware")
        
        # Initialize SPI
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0) # Bus 0, Device 0
            self.spi.max_speed_hz = 1000000 
        except Exception as e:
            self.logger.error(f"SPI init failed: {e}")
            return
        # Readers Configuration (BCM Pins)
        # SHARED RESET LOGIC: Toggle the shared RST pin (27) once globally
        rst_pin = 27
        try:
            GPIO.setup(rst_pin, GPIO.OUT)
            GPIO.output(rst_pin, GPIO.LOW)
            time.sleep(0.01) # 10ms reset
            GPIO.output(rst_pin, GPIO.HIGH)
            time.sleep(0.05) # 50ms startup
            self.logger.info("Global RFID Reset performed on Pin 27")
        except Exception as e:
            self.logger.error(f"Global Reset failed: {e}")

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
                reader = RfidReader(
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
