import RPi.GPIO as GPIO
from .LightDelegate import LightDelegate

class LightSensor:
    def __init__(self, pin: int, delegate: LightDelegate, threshold: int = 1000, name: str = "LightSensor"):
        """Initialize light sensor.
        
        Args:
            pin: GPIO pin (BCM)
            delegate: Callback handler
            threshold: Ignored in Digital Mode (Pi)
            name: Sensor identifier
        """
        if not isinstance(delegate, LightDelegate):
            raise TypeError("delegate must be an instance of LightDelegate")
        
        self.pin = pin
        self.delegate = delegate
        self.name = name
        self.threshold = threshold # Kept for API compatibility
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def read(self) -> int:
        """Read current light level and notify delegate.
        
        On Raspberry Pi (Digital), returns:
        - 4095 if HIGH (Light detected usually, depending on sensor)
        - 0 if LOW
        """
        # Read digital state
        state = GPIO.input(self.pin)
        
        # Map 0/1 to 0/4095 to simulate ADC for existing logic
        value = 4095 if state else 0
        
        # Logic: is triggered if value > threshold?
        # If signal is reversed (Light = 0), this logic might need inversion.
        # Assuming typical digital sensor: High = Active.
        triggered = value > self.threshold
        
        try:
            self.delegate.on_light_change(value, triggered, self.name)
        except Exception as e:
            print(f"Error in Light delegate: {e}")
        
        return value

    def is_bright(self) -> bool:
        """Check if current light level exceeds threshold."""
        return GPIO.input(self.pin) == 1
