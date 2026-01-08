"""Camera module - handles webcam capture and listing."""

import cv2
import os
from PIL import Image
from io import BytesIO


import threading

class Camera:
    """Manages webcam capture."""
    
    def __init__(self, index: int = 0):
        self.index = index
        self.cap = None
        self.lock = threading.RLock()
    
    def open(self) -> bool:
        """Open camera connection."""
        with self.lock:
            if self.cap is not None and self.cap.isOpened():
                return True
            try:
                self.cap = cv2.VideoCapture(self.index)
                return self.cap.isOpened()
            except:
                return False
    
    def close(self):
        """Close camera connection."""
        with self.lock:
            if self.cap:
                self.cap.release()
                self.cap = None
    
    def capture(self) -> bytes | None:
        """Capture a frame and return as JPEG bytes."""
        with self.lock:
            if not self.cap or not self.cap.isOpened():
                if not self.open():
                    return None
            
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    return None
                
                # Convert BGR to RGB
                if hasattr(self, '_config_loaded') is False:
                    from src.config import CAMERA_ZOOM, LOW_LIGHT_BOOST
                    self.zoom = CAMERA_ZOOM
                    self.boost = LOW_LIGHT_BOOST
                    self._config_loaded = True

                # 1. Low Light Boost (CLAHE)
                if self.boost:
                    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                    cl = clahe.apply(l)
                    limg = cv2.merge((cl,a,b))
                    frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

                # 2. Digital Zoom (Center Crop)
                if self.zoom > 1.0:
                    h, w = frame.shape[:2]
                    # Safety check
                    if h > 0 and w > 0:
                        new_h, new_w = int(h / self.zoom), int(w / self.zoom)
                        if new_h > 10 and new_w > 10:
                            top = (h - new_h) // 2
                            left = (w - new_w) // 2
                            frame = frame[top:top+new_h, left:left+new_w]
                        else:
                            print(f"Zoom skipped: Frame too small ({w}x{h})")
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                
                # Return as JPEG bytes
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Capture error: {e}")
                return None
    
    def get_frame_for_display(self):
        """Get frame as RGB for tkinter display."""
        with self.lock:
            if not self.cap or not self.cap.isOpened():
                if not self.open():
                    return None
            
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    return None
                
                # Apply same transforms for consistency
                if not hasattr(self, '_config_loaded'):
                     from src.config import CAMERA_ZOOM, LOW_LIGHT_BOOST
                     self.zoom = CAMERA_ZOOM
                     self.boost = LOW_LIGHT_BOOST
                     self._config_loaded = True
                
                if self.boost:
                    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    cl = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                    limg = cv2.merge((cl,a,b))
                    frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
                    
                if self.zoom > 1.0:
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h / self.zoom), int(w / self.zoom)
                    top = (h - new_h) // 2
                    left = (w - new_w) // 2
                    frame = frame[top:top+new_h, left:left+new_w]
                
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except:
                return None


def list_cameras(max_check: int = 5) -> list[tuple[int, str]]:
    """
    List available cameras.
    Returns list of (index, name).
    """
    # Try to get names via system_profiler (macOS only)
    names = {}
    try:
        import subprocess
        cmd = ["system_profiler", "SPCameraDataType", "-json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        
        items = data.get('SPCameraDataType', [])
        for i, item in enumerate(items):
            # Map index to name (assuming order matches OpenCV)
            names[i] = item.get('_name', f"Camera {i}")
            
    except Exception:
        pass

    # Suppress OpenCV errors
    os.environ["OPENCV_LOG_LEVEL"] = "OFF"
    
    cameras = []
    for i in range(max_check):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    name = names.get(i, f"Camera {i}")
                    cameras.append((i, name))
                cap.release()
        except:
            pass
    
    return cameras
