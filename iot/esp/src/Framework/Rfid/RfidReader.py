from machine import Pin
from libs.mfrc.mfrc522 import MFRC522
import time

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
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.rst = Pin(rst_pin, Pin.OUT)
        self.reader = MFRC522(spi, self.cs, self.rst)
        self.delegate = delegate
        self._last_uid = None
        self.last_scan_time = 0

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
            current_time = time.ticks_ms()
            # Allow re-trigger if different UID OR if 2 seconds passed since last trigger
            if uid != self._last_uid or time.ticks_diff(current_time, self.last_scan_time) > 2000:
                self._last_uid = uid
                self.last_scan_time = current_time
                try:
                    self.delegate.on_read(uid, self.name)
                except Exception as e:
                    print(f"Error in RFID delegate on_read: {e}")
        elif self._last_uid is not None:
            try:
                if hasattr(self.delegate, "on_card_lost"):
                    self.delegate.on_card_lost(self._last_uid, self.name)
            except Exception as e:
                print(f"Error in RFID delegate on_card_lost: {e}")

            self._last_uid = None

