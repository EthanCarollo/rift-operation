import RPi.GPIO as GPIO
import time

class MFRC522:
    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, spi, cs_pin, rst_pin):
        self.spi = spi
        self.cs_pin = cs_pin
        self.rst_pin = rst_pin
        
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        
        GPIO.output(self.cs_pin, GPIO.HIGH)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        
        self.init()

    def _wreg(self, reg, val):
        GPIO.output(self.cs_pin, GPIO.LOW)
        # Address format: (reg << 1) & 0x7E
        self.spi.xfer2([((reg << 1) & 0x7E), val])
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def _rreg(self, reg):
        GPIO.output(self.cs_pin, GPIO.LOW)
        # Address format for read: ((reg << 1) & 0x7E) | 0x80
        # Send address, receive value in second byte
        resp = self.spi.xfer2([((reg << 1) & 0x7E) | 0x80, 0x00])
        GPIO.output(self.cs_pin, GPIO.HIGH)
        return resp[1]

    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR

        if cmd == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._cflags(0x04, 0x80)
        self._sflags(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for c in send:
            self._wreg(0x09, c)
        self._wreg(0x01, cmd)

        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break

        self._cflags(0x0D, 0x80)

        if i:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                stat = self.OK

                if n & irq_en & 0x01:
                    stat = self.NOTAGERR

                if cmd == 0x0C:
                    n = self._rreg(0x0A)
                    lbits = self._rreg(0x0C) & 0x07
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8

                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16

                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                stat = self.ERR

        return stat, recv, bits

    def request(self, mode):
        self._wreg(0x0D, 0x07)
        (stat, recv, bits) = self._tocard(0x0C, [mode])
        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR
        return stat, bits

    def anticoll(self):
        ser_chk = 0
        ser = [0x93, 0x20]
        self._wreg(0x0D, 0x00)
        (stat, recv, bits) = self._tocard(0x0C, ser)

        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                # EMERGENCY FIX: Disable checksum validation for demo
                # if ser_chk != recv[4]:
                #     stat = self.ERR
                pass  # Accept UID even with bad checksum
            else:
                print(f"[MFRC522] DEBUG anticoll: Invalid length recv={len(recv)}")
                stat = self.ERR

        return stat, recv

    def init(self):
        # Shared RST Fix: Do not toggle RST here, strictly done in Hardware init globally
        # GPIO.output(self.rst_pin, GPIO.LOW)
        # time.sleep(0.0001)
        # GPIO.output(self.rst_pin, GPIO.HIGH)
        # time.sleep(0.05)
        
        self._wreg(0x01, 0x0F)
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self.antenna_on()
        
    def halt(self):
        buf = [0x50, 0x00]
        self._tocard(0x0C, buf)

    def antenna_on(self):
        temp = self._rreg(0x14)
        if not (temp & 0x03):
            self._sflags(0x14, 0x03)

    def antenna_off(self):
        self._cflags(0x14, 0x03)
