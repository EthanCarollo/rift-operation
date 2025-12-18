"""
RiftRfidDelegate.py - RFID callback delegate for Rift workshop
"""
from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class RiftRfidDelegate(RFIDDelegate):
    def __init__(self, workshop):
        self.workshop = workshop

    def on_read(self, uid, reader_name):
        print(f"[RFID] {reader_name} : LECTURE UUID - {uid}")
        if self.workshop:
            self.workshop.on_rfid_read(uid, reader_name)

    def on_card_lost(self, uid, reader_name):
        if self.workshop:
            self.workshop.on_rfid_lost(uid, reader_name)
