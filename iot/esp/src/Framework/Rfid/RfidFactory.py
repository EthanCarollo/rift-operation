from .RfidReader import RFIDReader

class RFIDFactory:
    """
    Factory pour créer plusieurs lecteurs RC522 sur un SPI commun.

    ⚠️ Commentaire matériel important :
    - SPI partagé :
        SCK  -> GPIO 18
        MOSI -> GPIO 23
        MISO -> GPIO 19
        3.3V -> 3.3V
        GND  -> GND

    (Exemple en dessous)

    - Lecteur 1 :
        CS (SDA) -> GPIO 32
        RST -> GPIO 33
        
    - Lecteur 2 (optionnel) :
        CS (SDA) -> GPIO 16
        RST -> GPIO 4

    - Lecteur 3 :
        CS (SDA) -> GPIO 17
        RST -> GPIO 21

    - Lecteur 4 :
        CS (SDA) -> GPIO 5
        RST -> GPIO 22
    """

    @staticmethod
    def create_reader(spi, cs_pin, rst_pin, delegate, name):
        """Crée un lecteur RC522 sur le SPI commun (CS = SDA)"""
        return RFIDReader(spi, cs_pin, rst_pin, delegate, name)

    @staticmethod
    def create_multiple_readers(spi, readers_config):
        """
        Crée plusieurs lecteurs à partir d'une liste de configs.
        readers_config = [
            {"cs":5, "rst":22, "delegate":Delegate1(), "name":"Lecteur1"},
            {"cs":17, "rst":21, "delegate":Delegate2(), "name":"Lecteur2"},
        ]
        (CS = SDA)
        """
        readers = []
        for cfg in readers_config:
            reader = RFIDReader(
                spi,
                cfg["cs"],
                cfg["rst"],
                cfg["delegate"],
                cfg.get("name", "RFID")
            )
            readers.append(reader)
        return readers