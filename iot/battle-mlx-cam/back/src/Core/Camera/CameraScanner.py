import os
import cv2
import subprocess
import json

class CameraScanner:
    """
    Service to list available cameras.
    """
    
    @staticmethod
    def list_cameras(max_check: int = 3) -> list[tuple[int, str]]:
        """
        List available cameras.
        Returns list of (index, name).
        """
        # Try to get names via system_profiler (macOS only)
        names = {}
        if os.name == 'posix':
            try:
                cmd = ["system_profiler", "SPCameraDataType", "-json"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                data = json.loads(result.stdout)
                items = data.get('SPCameraDataType', [])
                
                # Adjust max_check based on actual hardware
                if items:
                    max_check = len(items)
                
                for i, item in enumerate(reversed(items)):
                     names[i] = item.get('_name', f"Camera {i}")
            except Exception:
                pass

        # Suppress OpenCV errors
        os.environ["OPENCV_LOG_LEVEL"] = "OFF"
        
        cameras = []
        for i in range(max_check + 1): 
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    name = names.get(i, f"Camera {i}")
                    cameras.append((i, name))
                    cap.release()
            except:
                pass
        
        return cameras
