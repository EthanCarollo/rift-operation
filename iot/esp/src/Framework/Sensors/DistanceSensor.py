from machine import Pin, time_pulse_us
import time

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trigger.value(0)

    def get_distance_cm(self):
        """Returns distance in cm or -1 if timeout"""
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        # Timeout 30ms (approx 5m)
        duration = time_pulse_us(self.echo, 1, 30000)
        
        if duration < 0:
            return -1
        
        # Speed of sound is 343m/s or 0.0343 cm/us
        # Distance = (duration * speed) / 2
        distance = (duration * 0.0343) / 2
        return distance
