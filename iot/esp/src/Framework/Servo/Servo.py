import machine

class Servo:
    def __init__(self, pin_id, freq=50, min_duty=26, max_duty=123):
        # min_duty and max_duty might need tuning for SG90 or similar
        # Standard: 0.5ms to 2.5ms pulse width
        # At 50Hz (20ms), 0.5ms is 2.5% duty, 2.5ms is 12.5% duty
        # 1024 * 0.025 = ~26
        # 1024 * 0.125 = ~128
        self.pwm = machine.PWM(machine.Pin(pin_id))
        self.pwm.freq(freq)
        self.min_duty = min_duty
        self.max_duty = max_duty

    def set_angle(self, angle):
        """Set angle between 0 and 180"""
        if angle < 0: angle = 0
        if angle > 180: angle = 180
        
        duty = int(self.min_duty + (angle / 180.0) * (self.max_duty - self.min_duty))
        self.pwm.duty(duty)
        
    def off(self):
        self.pwm.duty(0)
