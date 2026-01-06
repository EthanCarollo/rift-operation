import RPi.GPIO as GPIO
import time
from .DistanceDelegate import DistanceDelegate

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin, delegate, name="DistanceSensor"):
        if not isinstance(delegate, DistanceDelegate):
            raise TypeError("delegate must be an instance of DistanceDelegate")

        self.trigger = trigger_pin
        self.echo = echo_pin
        self.delegate = delegate
        self.name = name
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        
        GPIO.output(self.trigger, False)

    def measure(self):
        """Triggers measurement and calls delegate"""
        distance = self._get_distance_cm()
        if distance != -1:
            try:
                self.delegate.on_measure(distance, self.name)
            except Exception as e:
                print(f"Error in Distance delegate: {e}")
        return distance

    def _get_distance_cm(self):
        """Internal synchronous measurement"""
        # Trigger High for 10us
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)

        start_time = time.time()
        stop_time = time.time()
        
        timeout = start_time + 0.1 # 100ms timeout
        
        # Wait for Echo High
        while GPIO.input(self.echo) == 0:
            start_time = time.time()
            if start_time > timeout:
                return -1

        # Wait for Echo Low
        while GPIO.input(self.echo) == 1:
            stop_time = time.time()
            if stop_time > timeout:
                return -1

        elapsed = stop_time - start_time
        # Speed of sound 34300 cm/s
        distance = (elapsed * 34300) / 2
        
        return distance
