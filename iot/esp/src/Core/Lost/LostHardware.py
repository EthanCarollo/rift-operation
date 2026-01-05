"""
LostHardware.py - Wrapper for role-specific hardware
"""
from machine import SPI, Pin
try:
    from src.Framework.Servo.Servo import Servo
    from src.Framework.Distance.DistanceSensor import DistanceSensor
    from src.Framework.Rfid.RfidReader import RFIDReader
    from src.Framework.Button.Button import Button
    from src.Framework.Light.LightSensor import LightSensor
    
    from src.Core.Lost.LostServoDelegate import LostServoDelegate
    from src.Core.Lost.LostDistanceDelegate import LostDistanceDelegate
    from src.Core.Lost.LostRfidDelegate import LostRfidDelegate
    from src.Core.Lost.LostButtonDelegate import LostButtonDelegate
    from src.Core.Lost.LostLightDelegate import LostLightDelegate
except ImportError:
    pass 

class LostHardware:
    def __init__(self, config, controller, role):
        self.role = role
        self.logger = controller.logger
        self.controller = controller
        self.callback = None
        self.last_distance_poll = 0
        
        # Hardware containers
        self.servo = None
        self.distance = None
        self.rfid = None
        self.button = None
        self.light_sensor = None
        self.last_light_poll = 0
        
        # Delegates (instantiated here to be ready, but connected to workshop later)
        self.servo_delegate = LostServoDelegate(None)
        self.distance_delegate = LostDistanceDelegate(None)
        self.rfid_delegate = LostRfidDelegate(None)
        self.button_delegate = LostButtonDelegate(None)
        self.light_delegate = LostLightDelegate(None)
        
        self.init_hardware()

    def attach_callback(self, callback):
        self.callback = callback
        # Update delegates with the workshop
        self.servo_delegate.workshop = callback
        self.distance_delegate.workshop = callback
        self.rfid_delegate.workshop = callback
        self.button_delegate.workshop = callback
        self.light_delegate.workshop = callback

    def update(self):
        if self.role == "dream":
            if self.rfid:
                self.rfid.check()
            
            # Poll distance every 200ms
            if self.distance and self.callback:
                 import time
                 if time.ticks_diff(time.ticks_ms(), self.last_distance_poll) > 200:
                     self.last_distance_poll = time.ticks_ms()
                     self.distance.measure()
        
        elif self.role == "nightmare":
            # Poll light sensor every 200ms
            if self.light_sensor and self.callback:
                import time
                if time.ticks_diff(time.ticks_ms(), self.last_light_poll) > 200:
                    self.last_light_poll = time.ticks_ms()
                    self.light_sensor.read()

    def get_distance(self):
        if self.distance:
            return self.distance.measure()
        return -1

    def set_servo(self, angle):
        if self.servo:
            self.servo.set_angle(angle)

    def init_hardware(self):
        self.logger.info(f"Initializing Hardware for Role: {self.role}")
        
        if self.role == "dream":
            # Dream: Servo (32), Distance (Trig 25, Echo 33), RFID (SPI), Button (35)
            # Distance
            try:
                self.distance = DistanceSensor(trigger_pin=25, echo_pin=33, 
                                             delegate=self.distance_delegate, name="WallSensor")
                # self.logger.info("Distance Sensor initialized (T:25, E:33)")
            except Exception as e:
                self.logger.error(f"Distance init failed: {e}")
            # Servo
            try:
                self.servo = Servo(pin_id=32, delegate=self.servo_delegate, name="DreamServo")
                # self.logger.info("Servo initialized (32)")
            except Exception as e:
                self.logger.error(f"Servo init failed: {e}")
            # RFID
            try:
                sck = 18; mosi = 17; miso = 19; cs = 5; rst = 21
                spi = SPI(2, baudrate=2500000, polarity=0, phase=0, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
                self.rfid = RFIDReader(spi, cs, rst, self.rfid_delegate, name="DreamReader")
                # self.logger.info("RFID initialized")
            except Exception as e:
                self.logger.error(f"RFID init failed: {e}")
            # Button
            try:
                self.button = Button(pin_id=26, delegate=self.button_delegate)
                # self.logger.info("Button initialized (26)")
            except Exception as e:
                self.logger.error(f"Button init failed: {e}")

        elif self.role == "nightmare":
            # Nightmare: Servo (2), Light Sensor (34)
            try:
                self.servo = Servo(pin_id=2, delegate=self.servo_delegate, name="NightmareServo")
                # self.logger.info("Servo initialized (2)")
            except Exception as e:
                self.logger.error(f"Servo init failed: {e}")
            # Light Sensor (TEMT6000)
            try:
                self.light_sensor = LightSensor(pin=34, delegate=self.light_delegate, 
                                               threshold=300, name="TEMT6000")
                self.logger.info("Light Sensor initialized (34)")
            except Exception as e:
                self.logger.error(f"Light sensor init failed: {e}")
