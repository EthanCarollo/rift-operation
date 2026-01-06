import machine, neopixel
import uasyncio as asyncio
import time

class LedStrip:
    """
    A class to control a NeoPixel (WS2812) LED strip using MicroPython and uasyncio.
    Supports basic color setting and asynchronous effects.
    """
    def __init__(self, pin_id, num_pixels):
        """
        Initialize the LED strip.
        :param pin_id: The GPIO pin number connected to the strip data line.
        :param num_pixels: The number of LEDs in the strip.
        """
        self.pin = machine.Pin(pin_id)
        self.num_pixels = num_pixels
        self.np = neopixel.NeoPixel(self.pin, num_pixels)
        self._effect_task = None
        self.clear()

    def set_pixel(self, index, color):
        """
        Set a single pixel color. Does NOT show immediately.
        :param index: Pixel index
        :param color: Tuple of (r, g, b) or (r, g, b, a) where a is 0.0-1.0 alpha/intensity
        """
        if len(color) == 4:
            r, g, b, a = color
            # Apply alpha directly as intensity multiplier
            r = int(r * a)
            g = int(g * a)
            b = int(b * a)
            self.np[index] = (r, g, b)
        else:
            self.np[index] = color

    def fill(self, color):
        """Set all pixels to the same color. Does NOT show immediately."""
        self.np.fill(color)

    def show(self):
        """Write the data to the strip."""
        self.np.write()

    def clear(self):
        """Turn off all pixels and show."""
        self.fill((0, 0, 0))
        self.show()

    def stop_effect(self):
        """Stop any running asynchronous effect."""
        if self._effect_task:
            self._effect_task.cancel()
            self._effect_task = None

    async def blink(self, color, on_ms, off_ms):
        """
        Blink the entire strip with a specific color.
        """
        self.stop_effect()
        self._effect_task = asyncio.create_task(self._blink_loop(color, on_ms, off_ms))

    async def _blink_loop(self, color, on_ms, off_ms):
        try:
            while True:
                self.fill(color)
                self.show()
                await asyncio.sleep_ms(on_ms)
                self.clear()
                await asyncio.sleep_ms(off_ms)
        except asyncio.CancelledError:
            self.clear()
            pass

    async def rainbow_cycle(self, wait_ms=20):
        """
        Start a rainbow cycle effect.
        """
        self.stop_effect()
        self._effect_task = asyncio.create_task(self._rainbow_loop(wait_ms))

    def _wheel(self, pos):
        """Internal helper to generate rainbow colors."""
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

    async def _rainbow_loop(self, wait_ms):
        try:
            while True:
                for j in range(255):
                    for i in range(self.num_pixels):
                        pixel_index = (i * 256 // self.num_pixels) + j
                        self.np[i] = self._wheel(pixel_index & 255)
                    self.show()
                    await asyncio.sleep_ms(wait_ms)
        except asyncio.CancelledError:
            self.clear()
            pass
