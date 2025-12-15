from machine import Pin
import time
from .ButtonDelegate import ButtonDelegate

class Button:
    def __init__(self, pin_id, delegate, trigger=Pin.IRQ_FALLING, pull=Pin.PULL_UP, debounce_delay=50):
        if not isinstance(delegate, ButtonDelegate):
            raise TypeError("delegate must be an instance of ButtonDelegate")

        self.pin = Pin(pin_id, mode=Pin.IN, pull=pull)
        self.delegate = delegate
        self.debounce_delay = debounce_delay
        self.last_click_time = 0

        self.pin.irq(trigger=trigger, handler=self._handle_irq)

    def _handle_irq(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_click_time) > self.debounce_delay:
            self.last_click_time = current_time
            self._trigger_delegate()

    def _trigger_delegate(self):
        try:
            self.delegate.on_click()
        except Exception as e:
            print(f"Error in Button delegate: {e}")
