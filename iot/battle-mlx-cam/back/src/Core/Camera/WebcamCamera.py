import cv2
import threading
from io import BytesIO
from PIL import Image
from src.Framework.Camera.AbstractCamera import AbstractCamera

class WebcamCamera(AbstractCamera):
    """
    Concrete implementation of a Webcam using OpenCV.
    """
    
    def __init__(self, index: int = 0):
        self.index = index
        self.cap = None
        self.lock = threading.RLock()
        
    def open(self) -> bool:
        with self.lock:
            if self.cap is not None and self.cap.isOpened():
                return True
            try:
                # Setup specific API backends if needed (e.g. CAP_AVFOUNDATION on mac)
                # But standard 0 is usually fine or handled by OpenCV internal auto-detect
                self.cap = cv2.VideoCapture(self.index)
                return self.cap.isOpened()
            except:
                return False

    def close(self):
        with self.lock:
            if self.cap:
                self.cap.release()
                self.cap = None

    def capture(self, settings: dict = None) -> bytes | None:
        """
        Capture frame with optional processing settings:
        - jpeg_quality (int, 1-100)
        - capture_scale (float, 0.1-1.0)
        - denoise_strength (int, 0-10)
        - zoom (float, >= 1.0)
        - low_light_boost (bool)
        """
        settings = settings or {}
        
        with self.lock:
            if not self.cap or not self.cap.isOpened():
                if not self.open():
                    return None
            
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    return None

                # --- 1. Settings Extraction ---
                jpeg_quality = settings.get('jpeg_quality', 85)
                scale = settings.get('capture_scale', 1.0)
                denoise = settings.get('denoise_strength', 0)
                zoom = settings.get('zoom', 1.0)
                boost = settings.get('low_light_boost', False)

                # --- 2. Processing ---
                
                # Scale
                if scale < 1.0 and scale > 0:
                    h, w = frame.shape[:2]
                    new_w, new_h = int(w * scale), int(h * scale)
                    if new_w > 10 and new_h > 10:
                        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

                # Low Light Boost (CLAHE)
                if boost:
                    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                    cl = clahe.apply(l)
                    limg = cv2.merge((cl,a,b))
                    frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

                # Denoise
                if denoise > 0:
                    frame = cv2.fastNlMeansDenoisingColored(frame, None, denoise, denoise, 7, 21)

                # Zoom (Center Crop)
                if zoom > 1.0:
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h / zoom), int(w / zoom)
                    if new_h > 10 and new_w > 10:
                        top = (h - new_h) // 2
                        left = (w - new_w) // 2
                        frame = frame[top:top+new_h, left:left+new_w]

                # --- 3. Encoding ---
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=jpeg_quality)
                return buffer.getvalue()

            except Exception as e:
                print(f"[WebcamCamera] Capture error: {e}")
                return None
