from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class CosmoRFIDDelegate(RFIDDelegate) :

    DARK_COSMO_RFID = "03-CD-14-AC-76"

    def __init__(self, callback=None):
        self.callback = callback

    def on_read(self, uid, reader_name):
        if uid == self.DARK_COSMO_RFID:
            self.callback.on_dark_cosmo_detected()
        pass

    def on_card_lost(self, uid, reader_name):
        if uid == self.DARK_COSMO_RFID:
            self.callback.on_dark_cosmo_lost()
        pass
