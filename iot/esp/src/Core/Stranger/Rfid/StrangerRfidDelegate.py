from src.Framework.Rfid.RfidDelegate import RFIDDelegate

class StrangerRFIDDelegate(RFIDDelegate) :
    P_LETTER = "13-F6-9B-0F-71"
    A_LETTER = "F3-4B-54-13-FF"
    U_LETTER = "E3-6A-75-AD-51"
    L_LETTER = "C3-BF-C0-2F-93"

    def on_read(self, uid, reader_name):
        """
        Le but ici, ça va être de pour chaque UID scanné, de check si tout est OK ou pas et si le nom est bon
        """
        print("Read : " + reader_name + " UID : " + uid)

    def on_card_lost(self, uid, reader_name):
        print("Card lost : " + reader_name + " UID : " + uid)
