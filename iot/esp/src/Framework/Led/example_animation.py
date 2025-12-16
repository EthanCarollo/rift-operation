import uasyncio as asyncio
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController

# Config
STRIP_PIN = 4
NUM_PIXELS = 12

# Example Animation JSON (Police lights style + Gradient)
ANIMATION = {
    "name": "Police & Gradient",
    "frames": [
        {
            "time": 200,
            "colors": [
                {"color": "255,0,0", "position": 0},
                {"color": "255,0,0", "position": 45},
                {"color": "0,0,0", "position": 50},
                {"color": "0,0,255", "position": 55},
                {"color": "0,0,255", "position": 100}
            ]
        },
        {
            "time": 200,
            "colors": [
                {"color": "0,0,255", "position": 0},
                {"color": "0,0,255", "position": 45},
                {"color": "0,0,0", "position": 50},
                {"color": "255,0,0", "position": 55},
                {"color": "255,0,0", "position": 100}
            ]
        },
        {
            "time": 1000,
            "colors": [
                {"color": "255,0,0", "position": 0},
                {"color": "0,255,0", "position": 50},
                {"color": "0,0,255", "position": 100}
            ]
        }
    ]
}

async def main():
    print("Initializing...")
    strip = LedStrip(STRIP_PIN, NUM_PIXELS)
    player = LedController(strip)

    print("Playing animation looping...")
    await player.play(ANIMATION, loop=True)
    
    # Keep the event loop running to allow the background task to execute
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
