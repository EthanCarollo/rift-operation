"""
LightDelegate.py - Abstract delegate for light sensor events
"""

class LightDelegate:
    def on_light_change(self, value: int, triggered: bool, sensor_name: str):
        """Called when light level is read.
        
        Args:
            value: Raw ADC value (0-4095)
            triggered: True if value exceeds threshold
            sensor_name: Identifier for the sensor
        """
        pass
