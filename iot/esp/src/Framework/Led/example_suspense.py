import uasyncio as asyncio
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController

# Config
STRIP_PIN = 4
NUM_PIXELS = 12

# "Suspense" Breathing Animation
# Smoothly pulses between very dim and moderately bright red (or any color).
# We use the Alpha channel to control the "brightness" of the animation dynamically.
SUSPENSE_ANIM = {
    "name": "Suspense Breathing",
    "frames": [
        {
            # State 1: Almost dark (Breathing Out)
            # Duration to transition to NEXT state (Peaking)
            "time": 3000, 
            "colors": [
                {"color": "255,0,0,0.05", "position": 0},   # Deep Red, 5% opacity
                {"color": "255,0,0,0.05", "position": 100}
            ]
        },
        {
            # State 2: Brighter (Breathing In)
            # Duration to transition back to START (Dark)
            "time": 3000,
            "colors": [
                {"color": "255,0,0,0.6", "position": 0},    # Deep Red, 60% opacity
                {"color": "255,0,0,0.6", "position": 100}
            ]
        }
    ]
}

async def main():
    print("Initializing Suspense Effect...")
    strip = LedStrip(STRIP_PIN, NUM_PIXELS)
    player = LedController(strip)
    
    # Optional: Set global brightness limit if needed
    # player.set_brightness(1.0) 

    print("Playing breathing animation...")
    await player.play(SUSPENSE_ANIM, loop=True)
    
    # Keep the event loop running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
