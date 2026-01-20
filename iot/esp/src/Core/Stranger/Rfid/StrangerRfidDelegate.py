from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class StrangerRFIDDelegate(RFIDDelegate) :
    P_LETTER = "9C-A7-BA-2A-AB"
    A_LETTER = "83-FC-3C-13-50"
    U_LETTER = "33-A7-83-0E-19"
    L_LETTER = "F3-45-F6-F4-B4"

    UID_MAP = {
        P_LETTER: "P",
        A_LETTER: "A",
        U_LETTER: "U",
        L_LETTER: "L"
    }

    def __init__(self, callback=None):
        self.callback = callback

    def on_read(self, uid, reader_name):
        print(uid)
        letter = self.UID_MAP.get(uid)
        if letter and self.callback:
            self.callback.on_letter_detected(reader_name, letter)

    def on_card_lost(self, uid, reader_name):
        if self.callback:
            self.callback.on_letter_lost(reader_name)

