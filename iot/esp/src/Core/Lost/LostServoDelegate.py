from src.Framework.Servo.ServoDelegate import ServoDelegate

class LostServoDelegate(ServoDelegate):
    def __init__(self, workshop):
        self.workshop = workshop

    def on_angle_changed(self, angle, name):
        if self.workshop and hasattr(self.workshop, "on_servo_event"):
             self.workshop.on_servo_event(angle, name)
