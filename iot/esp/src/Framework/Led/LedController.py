import time
import math
import ujson
import _thread
from src.Framework.Led.LedStrip import LedStrip

class LedController:
    """
    Plays JSON-based animations on a LedStrip.
    Handles color interpolation (gradients) and smooth transitions (LERP) between frames.
    Threaded version using _thread and Lock.
    """
    def __init__(self, strip: LedStrip):
        self.strip = strip
        self.is_playing = False
        self.brightness = 1.0
        self.lock = _thread.allocate_lock()
        
        # Animation state
        self.rendered_frames = []
        self.loop = False
        self.current_frame_idx = 0
        self.frame_start_time = 0
        self.num_frames = 0
        self.frames_data = []

    def start_thread(self):
        """Start the background animation thread."""
        _thread.start_new_thread(self._thread_loop, ())

    def _thread_loop(self):
        while True:
            try:
                self.update()
            except Exception as e:
                print(f"LedController thread error: {e}")
            time.sleep(0.010)

    def set_brightness(self, value: float):
        """Set global brightness (0.0 to 1.0)."""
        with self.lock:
            self.brightness = max(0.0, min(1.0, value))

    def stop(self):
        """Stop the current animation."""
        with self.lock:
            self.is_playing = False

    def play(self, animation_data, loop=True):
        """
        Setup an animation defined by animation_data dictionary.
        """
        frames = animation_data.get("frames", [])
        if not frames:
            return

        # Extract brightness, default to 1.0
        brightness = animation_data.get("brightness", 1.0)
        self.set_brightness(float(brightness))

        # Pre-calculate
        rendered = []
        for frame in frames:
            rendered.append(self._calculate_frame_pixels(frame))
        
        with self.lock:
            self.rendered_frames = rendered
            self.frames_data = frames
            self.num_frames = len(frames)
            self.current_frame_idx = 0
            self.loop = loop
            self.is_playing = True
            self.frame_start_time = time.ticks_ms()
            
            # Render initial state immediately
            if self.num_frames > 0:
                self._render_pixels(self.rendered_frames[0])

    def play_from_json(self, file_path, loop=True):
        """
        Load an animation from a JSON file and play it.
        """
        try:
            with open(file_path, "r") as f:
                data = ujson.load(f)
            self.play(data, loop)
        except Exception as e:
            print(f"Error loading animation from {file_path}: {e}")

    def update(self):
        """
        Update the animation state. Called by background thread.
        """
        # Quick check without lock first? No, safer with lock for is_playing
        with self.lock:
            if not self.is_playing or self.num_frames == 0:
                return

            now = time.ticks_ms()
            
            # Get duration of current frame
            duration = self.frames_data[self.current_frame_idx].get("time", 500)
            
            # Check if we need to advance to next frame
            elapsed = time.ticks_diff(now, self.frame_start_time)
            
            if elapsed >= duration:
                # Advance frame
                next_idx = self.current_frame_idx + 1
                
                if next_idx >= self.num_frames:
                    if self.loop:
                        next_idx = 0
                    else:
                        self.is_playing = False
                        return

                self.current_frame_idx = next_idx
                self.frame_start_time = now
                elapsed = 0 # Reset elapsed for new frame
                
            # Interpolation
            current_pixel_target = self.rendered_frames[self.current_frame_idx]
            
            next_idx = (self.current_frame_idx + 1) % self.num_frames
            if not self.loop and next_idx == 0 and self.current_frame_idx == self.num_frames - 1:
                 # Last frame, no loop. Just hold current.
                 next_pixel_target = current_pixel_target
            else:
                 next_pixel_target = self.rendered_frames[next_idx]

            # Calculate alpha (0.0 to 1.0)
            if duration > 0:
                alpha = elapsed / duration
            else:
                alpha = 1.0
            
            if alpha > 1.0: alpha = 1.0
            
            # Render logic (inside lock because strip might trigger SPI which might need protection if shared.. 
            # wait, strip is usually bitbang or RMT, but if it shares resources... 
            # LedStrip usually uses NeoPixel lib which disables interrupts. Should be fine.)
            mixed_pixels = []
            for i in range(self.strip.num_pixels):
                c1 = current_pixel_target[i]
                c2 = next_pixel_target[i]
                
                r = int(c1[0] + (c2[0] - c1[0]) * alpha)
                g = int(c1[1] + (c2[1] - c1[1]) * alpha)
                b = int(c1[2] + (c2[2] - c1[2]) * alpha)
                a = int(c1[3] + (c2[3] - c1[3]) * alpha)
                mixed_pixels.append((r, g, b, a))
            
            self._render_pixels(mixed_pixels)

    def _render_pixels(self, pixels):
        for i, color in enumerate(pixels):
            # color is (r, g, b, a)
            alpha_factor = color[3] / 255.0
            total_factor = self.brightness * alpha_factor
            
            r = int(color[0] * total_factor)
            g = int(color[1] * total_factor)
            b = int(color[2] * total_factor)
            self.strip.set_pixel(i, (r, g, b))
        self.strip.show()

    def _calculate_frame_pixels(self, frame):
        """
        Returns a list of (r,g,b,a) tuples for the strip based on frame gradients.
        """
        color_stops = frame.get("colors", [])
        num_pixels = self.strip.num_pixels
        result = [(0,0,0,0)] * num_pixels

        if not color_stops:
            return result

        stops = sorted(color_stops, key=lambda x: x.get("position", 0))

        # Parse colors
        parsed_stops = []
        for s in stops:
            try:
                c_str = s.get("color", "0,0,0")
                parts = list(map(float, c_str.split(',')))
                
                val_r = int(parts[0])
                val_g = int(parts[1])
                val_b = int(parts[2])
                
                val_a = 255
                if len(parts) > 3:
                    raw_a = parts[3]
                    if raw_a <= 1.0 and raw_a > 0:
                        val_a = int(raw_a * 255)
                    else:
                        val_a = int(raw_a)
                
                rgb = (val_r, val_g, val_b, val_a)
                pos = float(s.get("position", 0))
                parsed_stops.append((pos, rgb))
            except:
                pass
        
        if not parsed_stops:
            return result

        for i in range(num_pixels):
            pct = (i / (num_pixels - 1)) * 100 if num_pixels > 1 else 0
            
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
            a = int(start_stop[1][3] + (end_stop[1][3] - start_stop[1][3]) * ratio)
            result[i] = (r, g, b, a)
            
        return result
