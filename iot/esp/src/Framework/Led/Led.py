from machine import Pin
import uasyncio as asyncio

class Led:
    """
    A class to control an LED using MicroPython and uasyncio.
    Supports basic on/off/toggle and non-blocking blinking.
    """
    def __init__(self, pin_id, active_high=True):
        """
        Initialize the LED.
        :param pin_id: The GPIO pin number.
        :param active_high: True if high logic turns the LED on, False otherwise.
        """
        self.pin = Pin(pin_id, Pin.OUT)
        self.active_high = active_high
        self._blink_task = None
        self.off() # Ensure off at start

    def on(self):
        """Turn the LED on."""
        self.pin.value(1 if self.active_high else 0)

    def off(self):
        """Turn the LED off."""
        self.pin.value(0 if self.active_high else 1)

    def value(self, v):
        """Set the LED to a specific value (0 or 1, relative to active_high)."""
        if v:
            self.on()
        else:
            self.off()

    def toggle(self):
        """Toggle the LED state."""
        self.pin.value(not self.pin.value())

    async def blink(self, on_ms, off_ms):
        """
        Start blinking the LED asynchronously.
        This cancels any existing blink task.
        :param on_ms: Duration in milliseconds for the LED to be on.
        :param off_ms: Duration in milliseconds for the LED to be off.
        """
        self.stop_blink()
        self._blink_task = asyncio.create_task(self._blink_loop(on_ms, off_ms))

    def stop_blink(self):
        """Stop the blinking task if running."""
        if self._blink_task:
            self._blink_task.cancel()
            self._blink_task = None
        self.off()

    async def _blink_loop(self, on_ms, off_ms):
        """Internal loop for blinking."""
        try:
            while True:
                self.on()
                await asyncio.sleep_ms(on_ms)
                self.off()
                await asyncio.sleep_ms(off_ms)
        except asyncio.CancelledError:
            self.off() # Ensure off when cancelled
            pass
