import uasyncio as asyncio
from src.Framework.Led.Led import Led

# Example configuration
LED_PIN = 2 # Example pin (usually built-in LED on ESP32/ESP8266)

async def main():
    print("Initializing LED...")
    led = Led(LED_PIN)

    print("LED On")
    led.on()
    await asyncio.sleep(1)

    print("LED Off")
    led.off()
    await asyncio.sleep(1)

    print("Blinking (Fast: 100ms on, 100ms off)")
    await led.blink(100, 100)
    await asyncio.sleep(3)

    print("Blinking (Slow: 500ms on, 500ms off)")
    await led.blink(500, 500) 
    await asyncio.sleep(3)

    print("Stop blinking")
    led.stop_blink()
    
    print("Done.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
