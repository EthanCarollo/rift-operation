import RPi.GPIO as GPIO
import time
from .ServoDelegate import ServoDelegate

class Servo:
    def __init__(self, pin_id, delegate, name="Servo", freq=50, min_duty=2.5, max_duty=12.5):
        """
        pin_id: BCM GPIO pin
        min_duty: Duty cycle % for 0 degrees (approx 2.5% for SG90)
        max_duty: Duty cycle % for 180 degrees (approx 12.5% for SG90)
        """
        if not isinstance(delegate, ServoDelegate):
            raise TypeError("delegate must be an instance of ServoDelegate")

        self.name = name
        self.pin = pin_id
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.pin, freq)
        self.pwm.start(0) # Start with 0 duty (off)
        
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.delegate = delegate
        self.current_angle = 0

    def set_angle(self, angle):
        """Set angle between 0 and 180"""
        if angle < 0: angle = 0
        if angle > 180: angle = 180
        
        # Calculate duty cycle percentage (0.0 to 100.0)
        duty = self.min_duty + (angle / 180.0) * (self.max_duty - self.min_duty)
        self.pwm.ChangeDutyCycle(duty)
        self.current_angle = angle
        
        # Give servo time to move then cut signal to stop jitter
        # Note: This is a blocking pause, might be undesirable for high freq updates
        # but prevents digital servos from buzzing.
        # time.sleep(0.3) 
        # self.pwm.ChangeDutyCycle(0) 
        
        try:
            self.delegate.on_angle_changed(angle, self.name)
        except Exception as e:
            print(f"Error in Servo delegate: {e}")
        
    def off(self):
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        self.pwm.stop()
