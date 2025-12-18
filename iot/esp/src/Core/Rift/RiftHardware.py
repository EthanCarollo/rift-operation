"""
RiftHardware.py - Hardware wrapper for RIFT workshop
"""
from machine import SPI, Pin
from src.Framework.Rfid.RfidFactory import RFIDFactory
from src.Core.Rift.RiftRfidDelegate import RiftRfidDelegate

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
        # SPI pins (ESP32 VSPI)
        self.spi = SPI(
            1,
            baudrate=100_000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(23),
            miso=Pin(19),
        )
        # RFID readers configuration (Dream only for now)
        configs = [
            {"name": "DreamSlot1", "cs": 5,  "rst": 27},
            {"name": "DreamSlot2", "cs": 17, "rst": 26},
            {"name": "DreamSlot3", "cs": 16, "rst": 25},
            # {"name": "NightmareSlot1", "cs": 5,  "rst": 27},
            # {"name": "NightmareSlot2", "cs": 17, "rst": 26},
            # {"name": "NightmareSlot3", "cs": 16, "rst": 25},
        ]

        self.readers = RFIDFactory.create_multiple_readers(
            self.spi,
            [
                {
                    "cs": cfg["cs"],
                    "rst": cfg["rst"],
                    "delegate": self.delegate,
                    "name": cfg["name"],
                }
                for cfg in configs
            ],
        )

        self.logger.info(f"{len(self.readers)} RFID readers initialized")

    def update(self):
        for reader in self.readers:
            try:
                reader.check()
            except Exception as e:
                self.logger.error(f"RFID error on {reader.name}: {e}")
