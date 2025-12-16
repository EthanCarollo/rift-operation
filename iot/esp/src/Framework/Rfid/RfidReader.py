from machine import Pin
from libs.mfrc.mfrc522 import MFRC522
import time

class RFIDReader:
    def __init__(self, spi, cs_pin, rst_pin, delegate, name="RFID", cooldown=1):
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
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.rst = Pin(rst_pin, Pin.OUT)
        self.reader = MFRC522(spi, self.cs, self.rst)
        self.delegate = delegate
        self._last_uid = None
        self._cooldown = cooldown

    def _read_uid(self):
        status, _ = self.reader.request(self.reader.REQIDL)
        if status == self.reader.OK:
            status, uid = self.reader.anticoll()
            if status == self.reader.OK:
                uid_str = "-".join("{:02X}".format(b) for b in uid)
                return uid_str
        return None

    def check(self):
        """À appeler régulièrement dans la boucle principale"""
        uid = self._read_uid()
        if uid and uid != self._last_uid:
            self._last_uid = uid
            try:
                self.delegate.on_read(uid, self.name)
            except Exception as e:
                print(f"Error in RFID delegate: {e}")
            time.sleep(self._cooldown)
        elif uid is None:
            self._last_uid = None
