import uasyncio as asyncio
import math
from src.Framework.Led.LedStrip import LedStrip

class LedController:
    """
    Plays JSON-based animations on a LedStrip.
    Handles color interpolation (gradients) and smooth transitions (LERP) between frames.
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
        Smoothly interpolates between frames.
        """
        self.stop()
        self.is_playing = True
        self._play_task = asyncio.create_task(self._animation_loop(animation_data, loop))

    async def _animation_loop(self, animation_data, loop):
        frames = animation_data.get("frames", [])
        if not frames:
            return

        # Pre-calculate what the strip should look like for each frame
        # This saves computation during the tight loop.
        # Structure: list of lists of (r, g, b) tuples
        rendered_frames = []
        for frame in frames:
            rendered_frames.append(self._calculate_frame_pixels(frame))

        current_frame_idx = 0
        num_frames = len(frames)
        
        # FPS for interpolation
        FPS = 30 
        frame_delay_ms = int(1000 / FPS)

        try:
            while self.is_playing:
                # Current frame data
                current_pixel_target = rendered_frames[current_frame_idx]
                
                # Next frame data (for interpolation target)
                next_idx = (current_frame_idx + 1) % num_frames
                if not loop and next_idx == 0 and num_frames > 1:
                     # End of animation if not looping
                     # Just render the final frame and hold? Or stop?
                     # Let's hold final frame state
                     self._render_pixels(current_pixel_target)
                     break

                next_pixel_target = rendered_frames[next_idx]
                
                # Duration of the CURRENT frame creates the transition time to the NEXT frame
                duration = frames[current_frame_idx].get("time", 500)
                if duration < frame_delay_ms: duration = frame_delay_ms # Avoid divide by zero

                steps = int(duration / frame_delay_ms)
                
                for step in range(steps + 1):
                    if not self.is_playing: break
                    
                    alpha = step / steps
                    
                    # Interpolate every pixel
                    mixed_pixels = []
                    for i in range(self.strip.num_pixels):
                        c1 = current_pixel_target[i]
                        c2 = next_pixel_target[i]
                        
                        r = int(c1[0] + (c2[0] - c1[0]) * alpha)
                        g = int(c1[1] + (c2[1] - c1[1]) * alpha)
                        b = int(c1[2] + (c2[2] - c1[2]) * alpha)
                        mixed_pixels.append((r, g, b))
                    
                    self._render_pixels(mixed_pixels)
                    await asyncio.sleep_ms(frame_delay_ms)

                current_frame_idx = next_idx
                
        except asyncio.CancelledError:
            pass
        finally:
            self.is_playing = False

    def _render_pixels(self, pixels):
        for i, color in enumerate(pixels):
            self.strip.set_pixel(i, color)
        self.strip.show()

    def _calculate_frame_pixels(self, frame):
        """
        Returns a list of (r,g,b) tuples for the strip based on frame gradients.
        """
        color_stops = frame.get("colors", [])
        num_pixels = self.strip.num_pixels
        result = [(0,0,0)] * num_pixels

        if not color_stops:
            return result

        stops = sorted(color_stops, key=lambda x: x.get("position", 0))

        # Parse colors
        parsed_stops = []
        for s in stops:
            try:
                c_str = s.get("color", "0,0,0")
                rgb = tuple(map(int, c_str.split(',')))
                pos = float(s.get("position", 0))
                parsed_stops.append((pos, rgb))
            except:
                pass
        
        if not parsed_stops:
            return result

        for i in range(num_pixels):
            pct = (i / (num_pixels - 1)) * 100 if num_pixels > 1 else 0
            
            # Interpolate spatial
            # Find bounds
            start_stop = parsed_stops[0]
            end_stop = parsed_stops[-1]
            
            if pct <= parsed_stops[0][0]:
                result[i] = parsed_stops[0][1]
                continue
            if pct >= parsed_stops[-1][0]:
                result[i] = parsed_stops[-1][1]
                continue
            
            for j in range(len(parsed_stops) - 1):
                if parsed_stops[j][0] <= pct <= parsed_stops[j+1][0]:
                    start_stop = parsed_stops[j]
                    end_stop = parsed_stops[j+1]
                    break
            
            dst = end_stop[0] - start_stop[0]
            if dst == 0:
                ratio = 0
            else:
                ratio = (pct - start_stop[0]) / dst
            
            r = int(start_stop[1][0] + (end_stop[1][0] - start_stop[1][0]) * ratio)
            g = int(start_stop[1][1] + (end_stop[1][1] - start_stop[1][1]) * ratio)
            b = int(start_stop[1][2] + (end_stop[1][2] - start_stop[1][2]) * ratio)
            result[i] = (r, g, b)
            
        return result
