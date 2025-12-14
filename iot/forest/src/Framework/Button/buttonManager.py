from machine import Pin
import time


class ButtonInput:
    # Debounced button with press/release events
    def __init__(self, pin, debounce_ms):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms

        self._last_value = self.button.value()
        self._last_change_ms = 0

    def update(self, now_ms):
        """
        Returns:
          - True for pressed
          - False for released
          - None for no change
        """
        current = self.button.value()
        if current == self._last_value:
            return None

        if time.ticks_diff(now_ms, self._last_change_ms) <= self.debounce_ms:
            return None

        self._last_change_ms = now_ms
        self._last_value = current
        return (current == 0)
