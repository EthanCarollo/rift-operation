"""
LostHardware.py - Wrapper for role-specific hardware
"""
from machine import SPI, Pin
try:
    from src.Framework.Servo.Servo import Servo
    from src.Framework.Sensors.DistanceSensor import DistanceSensor
    from src.Framework.Rfid.RfidReader import RFIDReader
except ImportError:
    pass # Will fail if files not uploaded yet, but used for type hints

class LostHardware:
    def __init__(self, config, controller):
        self.role = config.lost.role
        self.logger = controller.logger
        self.controller = controller
        self.callback = None
        
        # Hardware containers
        self.servo = None
        self.distance = None
        self.rfid = None
        
        self.init_hardware()

    def attach_callback(self, callback):
        self.callback = callback
        if self.rfid and self.rfid.delegate:
            self.rfid.delegate.workshop = callback # Hacky but works if callback is workshop

    def update(self):
        if self.role == "child":
            if self.rfid:
                self.rfid.check()
            if self.distance and self.callback:
                 # Poll distance occasionally? Or let state request it?
                 # Better: Let state polling it via workshop -> hardware
                 pass

    def get_distance(self):
        if self.distance:
            return self.distance.get_distance_cm()
        return -1

    def set_servo(self, angle):
        if self.servo:
            self.servo.set_angle(angle)

    def init_hardware(self):
        self.logger.info(f"Initializing Hardware for Role: {self.role}")
        
        if self.role == "child":
            # Child: Servo (32), Distance (Trig 25, Echo 33), RFID (SPI)
            
            # Distance
            try:
                self.distance = DistanceSensor(trigger_pin=25, echo_pin=33)
                self.logger.info("Distance Sensor initialized (T:25, E:33)")
            except Exception as e:
                self.logger.error(f"Distance init failed: {e}")

            # Servo
            try:
                self.servo = Servo(pin_id=32)
                self.logger.info("Servo initialized (32)")
            except Exception as e:
                self.logger.error(f"Servo init failed: {e}")

            # RFID
            try:
                # SDA (SS): 5, SCK: 18, MOSI: 23, MISO: 19, RST: 21
                sck = 18
                mosi = 23
                miso = 19
                cs = 5
                rst = 21
                spi = SPI(2, baudrate=2500000, polarity=0, phase=0, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
                
                from src.Framework.Rfid.RfidDelegate import RFIDDelegate
                class LostRfidDelegate(RFIDDelegate):
                    def __init__(self):
                        self.workshop = None
                    def on_read(self, uid, name):
                        if self.workshop:
                             # Async not easy here, but check() is sync
                             # We can call a sync method on workshop
                             # But workshop methods are async?
                             # For now, just print or store
                             print(f"RFID READ: {uid}")
                             if hasattr(self.workshop, "on_rfid_read"):
                                 self.workshop.on_rfid_read(uid)

                self.rfid = RFIDReader(spi, cs, rst, LostRfidDelegate(), name="ChildReader")
                self.logger.info("RFID initialized")
            except Exception as e:
                self.logger.error(f"RFID init failed: {e}")

        elif self.role == "parent":
            # Parent: Servo (2)
            try:
                self.servo = Servo(pin_id=2)
                self.logger.info("Servo initialized (2)")
            except Exception as e:
                self.logger.error(f"Servo init failed: {e}")
