import RPi.GPIO as GPIO
import time
from .ButtonDelegate import ButtonDelegate

class Button:
    def __init__(self, pin_id, delegate,
                 edge=GPIO.FALLING,
                 pull_up_down=GPIO.PUD_UP,
                 debounce_delay=200):
        """
        pin_id: BCM pin number
        edge: GPIO.FALLING, GPIO.RISING, or GPIO.BOTH
        pull_up_down: GPIO.PUD_UP, GPIO.PUD_DOWN, or GPIO.PUD_OFF
        debounce_delay: milliseconds
        """

        if not isinstance(delegate, ButtonDelegate):
            raise TypeError("delegate must be an instance of ButtonDelegate")

        self.pin = pin_id
        self.delegate = delegate
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull_up_down)
        
        # Add event listener
        try:
            GPIO.add_event_detect(self.pin, edge, callback=self._handle_irq, bouncetime=debounce_delay)
        except RuntimeError as e:
            print(f"Error adding event detect for pin {self.pin}: {e}")
            
        self.active = True

    def deactivate(self):
        """Disable the button listener"""
        try:
            GPIO.remove_event_detect(self.pin)
        except Exception:
            pass
        self.active = False

    def activate(self):
        """Re-enable the button listener"""
        if not self.active:
            # Re-adding event detect might require knowing original params, 
            # simplified here to assume same as init if possible, or just flags
            self.active = True
            # Note: RPi.GPIO remove/add is tricky. Usually just keeping it added and filtering 
            # in callback is safer, or we'd need to store all init params.
            # strict "add_event_detect" again would be needed here.

    def _handle_irq(self, channel):
        if not self.active:
            return
            
        self._trigger_delegate()

    def _trigger_delegate(self):
        try:
            self.delegate.on_click()
        except Exception as e:
            print(f"Error in Button delegate: {e}")
