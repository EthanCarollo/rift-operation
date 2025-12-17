from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class StrangerRFIDDelegate(RFIDDelegate) :
    P_LETTER = "13-F6-9B-0F-71"
    A_LETTER = "F3-4B-54-13-FF"
    U_LETTER = "E3-6A-75-AD-51"
    L_LETTER = "C3-BF-C0-2F-93"

    UID_MAP = {
        P_LETTER: "P",
        A_LETTER: "A",
        U_LETTER: "U",
        L_LETTER: "L"
    }

    def __init__(self, callback=None):
        self.callback = callback

    def on_read(self, uid, reader_name):
        letter = self.UID_MAP.get(uid)
        if letter and self.callback:
            self.callback.on_letter_detected(reader_name, letter)

    def on_card_lost(self, uid, reader_name):
        if self.callback:
            self.callback.on_letter_lost(reader_name)
