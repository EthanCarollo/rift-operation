"""Camera module - handles webcam capture and listing."""

import cv2
import os
from PIL import Image
from io import BytesIO


class Camera:
    """Manages webcam capture."""
    
    def __init__(self, index: int = 0):
        self.index = index
        self.cap = None
    
    def open(self) -> bool:
        """Open camera connection."""
        self.cap = cv2.VideoCapture(self.index)
        return self.cap.isOpened()
    
    def close(self):
        """Close camera connection."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def capture(self) -> bytes | None:
        """Capture a frame and return as JPEG bytes."""
        if not self.cap or not self.cap.isOpened():
            if not self.open():
                return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Return as JPEG bytes
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    def get_frame_for_display(self):
        """Get frame as RGB for tkinter display."""
        if not self.cap or not self.cap.isOpened():
            if not self.open():
                return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


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
