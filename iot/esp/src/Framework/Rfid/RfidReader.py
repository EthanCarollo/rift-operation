from machine import Pin
from libs.mfrc.mfrc522 import MFRC522

class RFIDReader:
    def __init__(self, spi, cs_pin, rst_pin, delegate, name="RFID"):
        """
        spi : objet SPI
        cs_pin : GPIO pour CS
        rst_pin : GPIO pour RST
        delegate : instance de RFIDDelegate
        name : nom du lecteur
        cooldown : anti-relecture en secondes
        """
        if not isinstance(delegate, type(delegate)) or not hasattr(delegate, "on_read"):
            raise TypeError("delegate must implement on_read(uid, reader_name)")

        self.name = name
        
        if isinstance(cs_pin, int):
            self.cs = Pin(cs_pin, Pin.OUT, value=1)
        else:
            self.cs = cs_pin
            
        if isinstance(rst_pin, int):
            self.rst = Pin(rst_pin, Pin.OUT)
        else:
            self.rst = rst_pin
        self.reader = MFRC522(spi, self.cs, self.rst)
        self.delegate = delegate
        self.check_connection()
        self._last_uid = None

    def check_connection(self):
        """Checks if the reader is physically connected by reading version register"""
        v = self.reader._rreg(0x37)
        if v == 0x00 or v == 0xFF:
             print(f"[{self.name}] Initialization FAILED (Version: 0x{v:02X}) - Check wiring!")
             self.version = v
             return False
        else:
             print(f"[{self.name}] Initialization OK (Version: 0x{v:02X})")
             self.version = v
             return True

    def _read_uid(self):
        status, _ = self.reader.request(self.reader.REQIDL)
        if status == self.reader.OK:
            status, uid = self.reader.anticoll()
            if status == self.reader.OK:
                uid_str = "-".join("{:02X}".format(b) for b in uid)
                return uid_str
        return None

    def check(self):
        uid = self._read_uid()

        if uid:
            if uid != self._last_uid :
                self._last_uid = uid
                try:
                    self.delegate.on_read(uid, self.name)
                except Exception as e:
                    print(f"Error in RFID delegate on_read: {e}")
            self.reader.halt()
        elif self._last_uid is not None:
            try:
                if hasattr(self.delegate, "on_card_lost"):
                    self.delegate.on_card_lost(self._last_uid, self.name)
            except Exception as e:
                print(f"Error in RFID delegate on_card_lost: {e}")

            self._last_uid = None
