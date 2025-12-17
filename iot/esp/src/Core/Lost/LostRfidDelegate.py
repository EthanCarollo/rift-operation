from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class LostRfidDelegate(RFIDDelegate):
    def __init__(self, workshop):
        self.workshop = workshop

    def on_read(self, uid, name):
        if self.workshop and hasattr(self.workshop, "on_rfid_read"):
             self.workshop.on_rfid_read(uid)

    def on_card_lost(self, uid, name):
        """Card lost event (not used but required by framework)"""
        pass
