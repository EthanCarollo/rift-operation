import machine
from .ServoDelegate import ServoDelegate


"""
Comment qu'on le connecte ?

Servo wire -> Connect to
Red	-> 5–6 V external power
Brown / Black -> GND (same GND as ESP32)
Yellow / Orange / White	-> ESP32 GPIO (PWM-capable)
"""
class Servo:
    def __init__(self, pin_id, delegate, name="Servo", freq=50, min_duty=26, max_duty=123):
        if not isinstance(delegate, ServoDelegate):
            raise TypeError("delegate must be an instance of ServoDelegate")

        self.pwm = machine.PWM(machine.Pin(pin_id))
        self.pwm.freq(freq)
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.delegate = delegate
        self.name = name
        self.current_angle = 0

    def set_angle(self, angle):
        """Set angle between 0 and 180"""
        if angle < 0: angle = 0
        if angle > 180: angle = 180
        
        duty = int(self.min_duty + (angle / 180.0) * (self.max_duty - self.min_duty))
        self.pwm.duty(duty)
        self.current_angle = angle
        
        try:
            self.delegate.on_angle_changed(angle, self.name)
        except Exception as e:
            print(f"Error in Servo delegate: {e}")
        
    def off(self):
        self.pwm.duty(0)
