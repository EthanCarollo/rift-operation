import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Expose Framework and Core
from .Framework import (
    AbstractEditor, AbstractBackgroundRemover, AbstractRecognizer, AbstractCamera,
    AbstractWebSocket, AbstractWebServer
)

from .Core import (
    FalFluxEditor, VisionBackgroundRemover, KNNRecognizer, WebcamCamera, CameraScanner,
    RiftWebSocket, BattleWebServer, Config,
    get_camera_settings, update_camera_settings, reset_camera_settings
)

# Backward Compatibility (for now)
def get_api_key():
    return Config.get_api_key()

def list_cameras(max_check=3):
    return CameraScanner.list_cameras(max_check)

Camera = WebcamCamera
