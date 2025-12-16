from machine import Pin, time_pulse_us
import time
from .DistanceDelegate import DistanceDelegate

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin, delegate, name="DistanceSensor"):
        if not isinstance(delegate, DistanceDelegate):
            raise TypeError("delegate must be an instance of DistanceDelegate")

        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trigger.value(0)
        self.delegate = delegate
        self.name = name

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
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        # Timeout 30ms (approx 5m)
        duration = time_pulse_us(self.echo, 1, 30000)
        
        if duration < 0:
            return -1
        
        distance = (duration * 0.0343) / 2
        return distance
