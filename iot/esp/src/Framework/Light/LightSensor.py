"""
LightSensor.py - TEMT6000 ambient light sensor driver
"""
from machine import Pin, ADC
from .LightDelegate import LightDelegate

class LightSensor:
    def __init__(self, pin: int, delegate: LightDelegate, threshold: int = 1000, name: str = "LightSensor"):
        """Initialize light sensor.
        
        Args:
            pin: ADC-capable GPIO pin (e.g., 34)
            delegate: Callback handler
            threshold: ADC value above which `triggered` is True (0-4095)
            name: Sensor identifier
        """
        if not isinstance(delegate, LightDelegate):
            raise TypeError("delegate must be an instance of LightDelegate")
        
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # Full range 0-3.3V
        self.adc.width(ADC.WIDTH_12BIT)  # 0-4095
        
        self.delegate = delegate
        self.threshold = threshold
        self.name = name
        self._last_triggered = False

    def read(self) -> int:
        """Read current light level and notify delegate.
        
        Returns:
            Raw ADC value (0-4095)
        """
        value = self.adc.read()
        triggered = value > self.threshold
        
        try:
            self.delegate.on_light_change(value, triggered, self.name)
        except Exception as e:
            print(f"Error in Light delegate: {e}")
        
        return value

    def is_bright(self) -> bool:
        """Check if current light level exceeds threshold."""
        return self.adc.read() > self.threshold
