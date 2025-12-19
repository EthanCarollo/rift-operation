"""
RiftHardwareRaspberry.py - Raspberry Pi 4B RFID handler
"""
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

from src.Core.Rift.RiftRfidDelegate import RiftRfidDelegate

class RiftHardwareRaspberry:
    def __init__(self, controller):
        self.logger = controller.logger
        self.controller = controller
        self.workshop = None
        self.delegate = RiftRfidDelegate(None)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.readers = {}
        self._init_hardware()

    def attach_workshop(self, workshop):
        self.workshop = workshop
        self.delegate.workshop = workshop

    def _init_hardware(self):
        self.logger.info("Initializing Raspberry RFID hardware")

        configs = {
            "DreamSlot1": 5,
            "DreamSlot2": 6,
            "DreamSlot3": 13,
            "NightmareSlot1": 19,
            "NightmareSlot2": 26,
            "NightmareSlot3": 21,
        }

        for name, cs_pin in configs.items():
            GPIO.setup(cs_pin, GPIO.OUT)
            self.readers[name] = SimpleMFRC522(reader_id=cs_pin)

        self.logger.info(f"{len(self.readers)} RFID readers ready")

    def update(self):
        """
        Non-blocking polling (much faster than ESP)
        """
        for name, reader in self.readers.items():
            try:
                id, _ = reader.read_no_block()
                if id:
                    uid = format(id, "X")
                    self.delegate.on_read(uid, name)
            except Exception as e:
                self.logger.error(f"RFID error on {name}: {e}")
