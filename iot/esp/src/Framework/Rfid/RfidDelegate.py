class RFIDDelegate:
    def on_read(self, uid, reader_name):
        print("Fonction on_read non implémenté.")
        pass

    def on_card_lost(self, uid, reader_name):
        print("Fonction on_card_lost non implémenté.")
        pass
