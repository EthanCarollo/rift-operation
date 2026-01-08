from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class CosmoRFIDDelegate(RFIDDelegate) :

    DARK_COSMO_RFID = "03-AC-89-0F-29"

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
