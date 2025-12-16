import uasyncio as asyncio
from src.Framework.Led.LedStrip import LedStrip

# Example configuration
STRIP_PIN = 4   # GPIO pin connected to NeoPixel Data In
NUM_PIXELS = 12 # Number of LEDs in the strip

async def main():
    print("Initializing LED Strip...")
    strip = LedStrip(STRIP_PIN, NUM_PIXELS)

    print("Red")
    strip.fill((255, 0, 0))
    strip.show()
    await asyncio.sleep(1)

    print("Green")
    strip.fill((0, 255, 0))
    strip.show()
    await asyncio.sleep(1)
    
    print("Blue")
    strip.fill((0, 0, 255))
    strip.show()
    await asyncio.sleep(1)

    print("Blinking Blue (500ms)")
    await strip.blink((0, 0, 255), 500, 500)
    await asyncio.sleep(5)

    print("Rainbow Cycle")
    await strip.rainbow_cycle(wait_ms=10)
    await asyncio.sleep(10)

    print("Stop effect")
    strip.stop_effect()
    
    print("Done.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
