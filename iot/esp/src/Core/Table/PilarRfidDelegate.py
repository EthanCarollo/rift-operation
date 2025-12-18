from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class PilarRfidDelegate(RFIDDelegate):
    def on_read(self, uid, reader_name):
        print("read uid:", uid, "from reader:", reader_name)

    def on_card_lost(self, uid, reader_name):
        print("lost uid:", uid, "from reader:", reader_name)