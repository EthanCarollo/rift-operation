"""
RiftHardware.py - Hardware wrapper for RIFT workshop
"""
from machine import SPI, Pin
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Rift.RiftRfidDelegate import RiftRfidDelegate

class DummyPin:
    OUT = 0
    IN = 1
    def __init__(self, *args, **kwargs): pass
    def init(self, *args, **kwargs): pass
    def value(self, *args, **kwargs): pass

class RiftHardware:
    def __init__(self, controller):
        self.logger = controller.logger
        self.controller = controller
        self.workshop = None
        self.spi = None
        self.readers = []
        self.delegate = RiftRfidDelegate(None)
        self.init_hardware()

    def attach_workshop(self, workshop):
        self.workshop = workshop
        self.delegate.workshop = workshop

    def init_hardware(self):
        self.logger.info("Initializing RIFT Hardware")

        # Manually Reset RC522 (Shared Pin)
        rst = Pin(27, Pin.OUT)
        rst.value(0)
        import time
        time.sleep(0.05)
        rst.value(1)
        time.sleep(0.05)
        
        # SPI pins (ESP32 VSPI)
        self.spi = SPI(
            2,
            baudrate=100_000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(23),
            miso=Pin(19),
        )
        # RFID readers configuration (Dream + Nightmare)
        # Use DummyPin() because we already reset them manually
        configs = [
            {"name": "DreamSlot1",     "cs": 4,   "rst": DummyPin()},
            {"name": "DreamSlot2",     "cs": 17,  "rst": DummyPin()},
            {"name": "DreamSlot3",     "cs": 16,  "rst": DummyPin()},
            {"name": "NightmareSlot1", "cs": 5,   "rst": DummyPin()},
            {"name": "NightmareSlot2", "cs": 13,  "rst": DummyPin()},
            {"name": "NightmareSlot3", "cs": 14,  "rst": DummyPin()},
        ]
        
        # Prepare full config with delegate
        full_configs = []
        for cfg in configs:
            full_configs.append({
                "cs": cfg["cs"],
                "rst": cfg["rst"],
                "delegate": self.delegate,
                "name": cfg["name"]
            })

        try:
            self.readers = RFIDFactory.create_multiple_readers(self.spi, full_configs)
            self.logger.info(f"Initialized {len(self.readers)} RFID readers")
        except Exception as e:
            self.logger.error(f"Failed to initialize RFID readers: {e}")
            self.readers = []

    def update(self):
        for reader in self.readers:
            try:
                reader.check()
            except Exception as e:
                self.logger.error(f"RFID error on {reader.name}: {e}")