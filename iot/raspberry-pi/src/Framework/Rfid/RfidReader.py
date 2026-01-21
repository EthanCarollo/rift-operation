from src.Framework.Rfid.MFRC522 import MFRC522
import time

class RfidReader:
    def __init__(self, spi, cs_pin, rst_pin, delegate, name="RFID"):
        """
        spi : spidev instance
        cs_pin : BCM GPIO for CS
        rst_pin : BCM GPIO for RST
        delegate : instance of RFIDDelegate
        """
        if not hasattr(delegate, "on_read"):
            raise TypeError("delegate must implement on_read(uid, reader_name)")

        self.name = name
        self.cs_pin = cs_pin
        self.rst_pin = rst_pin
        
        self.reader = MFRC522(spi, self.cs_pin, self.rst_pin)
        self.delegate = delegate
        self._last_uid = None
        
        # EMERGENCY FIX: Don't check connection here, done in RiftHardware retry loop
        # self.check_connection()

    def check_connection(self):
        v = self.reader._rreg(0x37)
        if v == 0x00 or v == 0xFF:
             print(f"[{self.name}] Initialization FAILED (Version: 0x{v:02X}) - Check wiring!")
             return False
        else:
             print(f"[{self.name}] Initialization OK (Version: 0x{v:02X})")
             return True

    def _read_uid(self):
        status, _ = self.reader.request(self.reader.REQIDL)
        if status == self.reader.OK:
            status, uid = self.reader.anticoll()
            if status == self.reader.OK:
                uid_str = "-".join("{:02X}".format(b) for b in uid)
                return uid_str
            else:
                # Debug: anticoll failed
                print(f"[{self.name}] DEBUG: anticoll failed (status={status})")
        else:
            # Debug: request failed (this is normal when no card present, so only print occasionally)
            pass
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
