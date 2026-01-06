import uasyncio as asyncio
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController

# Config
STRIP_PIN = 27
NUM_PIXELS = 12
print("easy run on : " + STRIP_PIN)
# Example Animation JSON (Police lights style + Gradient)
ANIMATION = {
    "name": "Police & Gradient",
    "frames": [
        {
            "time": 200,
            "colors": [
                {"color": "255,0,0,1.0", "position": 0},
                {"color": "255,0,0,0.2", "position": 45}, # Fade out
                {"color": "0,0,0,0.0", "position": 50},
                {"color": "0,0,255,0.2", "position": 55}, # Fade in blue
                {"color": "0,0,255,1.0", "position": 100}
            ]
        },
        {
            "time": 200,
            "colors": [
                {"color": "0,0,255,1.0", "position": 0},
                {"color": "0,0,255,0.2", "position": 45},
                {"color": "0,0,0,0.0", "position": 50},
                {"color": "255,0,0,0.2", "position": 55},
                {"color": "255,0,0,1.0", "position": 100}
            ]
        },
        {
            "time": 1000,
            "colors": [
                {"color": "255,0,0,0.5", "position": 0},   # Half brightness
                {"color": "0,255,0,1.0", "position": 50},  # Full brightness
                {"color": "0,0,255,0.5", "position": 100}  # Half brightness
            ]
        }
    ]
}

async def main():
    print("Initializing...")
    strip = LedStrip(STRIP_PIN, NUM_PIXELS)
    player = LedController(strip)
    
    # Set global brightness (0.0 to 1.0)
    # This acts as a master dimmer on top of the alpha channel.
    player.set_brightness(0.8)

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

