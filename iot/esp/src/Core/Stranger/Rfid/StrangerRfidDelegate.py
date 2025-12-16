from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class StrangerRFIDDelegate(RFIDDelegate) :
    def on_read(self, uid, reader_name):
        print("Read : " reader_name + " UID : " + uid)
        return super().on_read(uid, reader_name)
