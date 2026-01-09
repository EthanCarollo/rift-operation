import gc
import time
import ujson
import _thread
from src.Framework.Led.LedStrip import LedStrip

class LedController:
    """
    Plays JSON-based animations on a LedStrip.
    Handles color interpolation (gradients) and smooth transitions (LERP) between frames.
    Threaded version with memory management for ESP32.
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
        _thread.start_new_thread(self._thread_loop, ())

    def _thread_loop(self):
        while True:
            try:
                self.update()
            except Exception as e:
                print(f"LED err: {e}")
            time.sleep(0.010)

    def set_brightness(self, value: float):
        with self.lock:
            self.brightness = max(0.0, min(1.0, value))

    def stop(self):
        with self.lock:
            self.is_playing = False
            self._clear_animation_data()

    def _clear_animation_data(self):
        """Clear animation data to free memory."""
        self.rendered_frames = []
        self.frames_data = []
        self.num_frames = 0
        gc.collect()

    def play(self, animation_data, loop=True):
        frames = animation_data.get("frames", [])
        if not frames:
            return

        with self.lock:
            self.is_playing = False
            
            # Clear old data first
            self.rendered_frames = []
            self.frames_data = []
            gc.collect()
            
            # Pre-calculate frames
            rendered = []
            for frame in frames:
                rendered.append(self._calculate_frame_pixels(frame))
                gc.collect()
            
            self.rendered_frames = rendered
            self.frames_data = frames
            self.num_frames = len(frames)
            self.current_frame_idx = 0
            self.loop = loop
            self.frame_start_time = time.ticks_ms()
            self.is_playing = True
            
            if self.num_frames > 0:
                self._render_pixels(self.rendered_frames[0])

    def play_from_json(self, file_path, loop=True):
        gc.collect()
        try:
            with open(file_path, "r") as f:
                data = ujson.load(f)
            self.play(data, loop)
            data = None
            gc.collect()
        except Exception as e:
            print(f"Anim load err: {e}")
            gc.collect()

    def update(self):
        with self.lock:
            if not self.is_playing or self.num_frames == 0:
                return

            now = time.ticks_ms()
            duration = self.frames_data[self.current_frame_idx].get("time", 500)
            elapsed = time.ticks_diff(now, self.frame_start_time)
            
            if elapsed >= duration:
                next_idx = self.current_frame_idx + 1
                
                if next_idx >= self.num_frames:
                    if self.loop:
                        next_idx = 0
                    else:
                        self.is_playing = False
                        return

                self.current_frame_idx = next_idx
                self.frame_start_time = now
                elapsed = 0
                
            current_pixel_target = self.rendered_frames[self.current_frame_idx]
            
            next_idx = (self.current_frame_idx + 1) % self.num_frames
            if not self.loop and next_idx == 0 and self.current_frame_idx == self.num_frames - 1:
                next_pixel_target = current_pixel_target
            else:
                next_pixel_target = self.rendered_frames[next_idx]

            alpha = min(1.0, elapsed / duration) if duration > 0 else 1.0
            
            # Render with interpolation - reuse list to avoid allocations
            for i in range(self.strip.num_pixels):
                c1 = current_pixel_target[i]
                c2 = next_pixel_target[i]
                
                r = int(c1[0] + (c2[0] - c1[0]) * alpha)
                g = int(c1[1] + (c2[1] - c1[1]) * alpha)
                b = int(c1[2] + (c2[2] - c1[2]) * alpha)
                a = c1[3] + (c2[3] - c1[3]) * alpha
                
                final_alpha = a * self.brightness
                self.strip.set_pixel(i, (r, g, b, final_alpha))
            
            self.strip.show()

    def _render_pixels(self, pixels):
        for i, color in enumerate(pixels):
            r, g, b, a = color
            final_alpha = a * self.brightness
            self.strip.set_pixel(i, (r, g, b, final_alpha))
        self.strip.show()

    def _calculate_frame_pixels(self, frame):
        color_stops = frame.get("colors", [])
        num_pixels = self.strip.num_pixels
        result = [(0,0,0,0)] * num_pixels

        if not color_stops:
            return result

        stops = sorted(color_stops, key=lambda x: x.get("position", 0))

        parsed_stops = []
        for s in stops:
            try:
                c_str = s.get("color", "0,0,0")
                parts = list(map(float, c_str.split(',')))
                
                val_r = int(parts[0])
                val_g = int(parts[1])
                val_b = int(parts[2])
                
                val_a = 1.0
                if len(parts) > 3:
                    raw_a = parts[3]
                    val_a = raw_a / 255.0 if raw_a > 1.0 else raw_a
                
                rgba = (val_r, val_g, val_b, val_a)
                pos = float(s.get("position", 0))
                parsed_stops.append((pos, rgba))
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
            ratio = (pct - start_stop[0]) / dst if dst != 0 else 0
            
            r = int(start_stop[1][0] + (end_stop[1][0] - start_stop[1][0]) * ratio)
            g = int(start_stop[1][1] + (end_stop[1][1] - start_stop[1][1]) * ratio)
            b = int(start_stop[1][2] + (end_stop[1][2] - start_stop[1][2]) * ratio)
            a = start_stop[1][3] + (end_stop[1][3] - start_stop[1][3]) * ratio
            result[i] = (r, g, b, a)
            
        return result
