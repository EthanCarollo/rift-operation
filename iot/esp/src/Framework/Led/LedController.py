import uasyncio as asyncio
import math
from src.Framework.Led.LedStrip import LedStrip

class LedController:
    """
    Plays JSON-based animations on a LedStrip.
    Handles color interpolation (gradients) between defined positions.
    """
    def __init__(self, strip: LedStrip):
        self.strip = strip
        self._play_task = None
        self.is_playing = False

    def stop(self):
        """Stop the current animation."""
        self.is_playing = False
        if self._play_task:
            self._play_task.cancel()
            self._play_task = None

    async def play(self, animation_data, loop=True):
        """
        Play an animation defined by animation_data dictionary.
        :param animation_data: dict containing "frames" list.
        :param loop: bool, whether to loop the animation indefinitely.
        """
        self.stop()
        self.is_playing = True
        self._play_task = asyncio.create_task(self._animation_loop(animation_data, loop))

    async def _animation_loop(self, animation_data, loop):
        frames = animation_data.get("frames", [])
        if not frames:
            return

        try:
            while self.is_playing:
                for frame in frames:
                    duration = frame.get("time", 100)
                    color_stops = frame.get("colors", [])
                    
                    self._render_frame(color_stops)
                    
                    # Wait for the frame duration
                    await asyncio.sleep_ms(duration)
                
                if not loop:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            self.is_playing = False

    def _render_frame(self, color_stops):
        """
        Render a single frame's color gradient onto the strip.
        color_stops: list of dicts { "color": "r,g,b", "position": 0-100 }
        """
        if not color_stops:
            return

        # Sort stops by position just in case
        stops = sorted(color_stops, key=lambda x: x.get("position", 0))

        # Parse string colors "255,0,0" to tuples (255, 0, 0)
        parsed_stops = []
        for s in stops:
            try:
                c_str = s.get("color", "0,0,0")
                rgb = tuple(map(int, c_str.split(',')))
                pos = float(s.get("position", 0))
                parsed_stops.append((pos, rgb))
            except:
                pass # Skip invalid

        if not parsed_stops:
            return

        num_pixels = self.strip.num_pixels
        
        for i in range(num_pixels):
            # Calculate position of current pixel in % (0 - 100)
            pixel_pos_pct = (i / (num_pixels - 1)) * 100 if num_pixels > 1 else 0

            # Find the two stops surrounding this pixel
            start_stop = None
            end_stop = None

            # Handle edge cases: pixel before first stop or after last stop
            if pixel_pos_pct <= parsed_stops[0][0]:
                self.strip.set_pixel(i, parsed_stops[0][1])
                continue
            if pixel_pos_pct >= parsed_stops[-1][0]:
                self.strip.set_pixel(i, parsed_stops[-1][1])
                continue

            # Find bounding stops
            for j in range(len(parsed_stops) - 1):
                if parsed_stops[j][0] <= pixel_pos_pct <= parsed_stops[j+1][0]:
                    start_stop = parsed_stops[j]
                    end_stop = parsed_stops[j+1]
                    break
            
            if start_stop and end_stop:
                # Interpolate
                dst = end_stop[0] - start_stop[0]
                if dst == 0:
                    ratio = 0
                else:
                    ratio = (pixel_pos_pct - start_stop[0]) / dst
                
                r = int(start_stop[1][0] + (end_stop[1][0] - start_stop[1][0]) * ratio)
                g = int(start_stop[1][1] + (end_stop[1][1] - start_stop[1][1]) * ratio)
                b = int(start_stop[1][2] + (end_stop[1][2] - start_stop[1][2]) * ratio)
                self.strip.set_pixel(i, (r, g, b))

        self.strip.show()
