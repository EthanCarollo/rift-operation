"""
LostLightDelegate.py - Light sensor delegate for Lost workshop
"""
from src.Framework.Light.LightDelegate import LightDelegate

class LostLightDelegate(LightDelegate):
    def __init__(self, workshop):
        self.workshop = workshop

    def on_light_change(self, value, triggered, name):
        if self.workshop and hasattr(self.workshop, "on_light_event"):
            self.workshop.on_light_event(value, triggered, name)
