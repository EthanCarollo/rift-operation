from machine import Pin
from libs.mfrc.mfrc522 import MFRC522
import time

class RFIDDelegate:
    def on_read(self, uid, reader_name):
        """Appelé quand un badge est lu"""
        pass
