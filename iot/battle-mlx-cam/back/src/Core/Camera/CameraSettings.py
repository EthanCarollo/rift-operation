import threading
from src.Core.Config import Config

# Runtime settings (can be modified via web UI)
_camera_settings = {
    'jpeg_quality': Config.JPEG_QUALITY,
    'capture_scale': Config.CAPTURE_SCALE,
    'denoise_strength': Config.DENOISE_STRENGTH
}
_settings_lock = threading.Lock()

def get_camera_settings() -> dict:
    """Get current camera settings."""
    with _settings_lock:
        return _camera_settings.copy()

def update_camera_settings(settings: dict) -> dict:
    """Update camera settings. Returns the new settings."""
    with _settings_lock:
        if 'jpeg_quality' in settings:
            _camera_settings['jpeg_quality'] = max(1, min(100, int(settings['jpeg_quality'])))
        if 'capture_scale' in settings:
            _camera_settings['capture_scale'] = max(0.25, min(1.0, float(settings['capture_scale'])))
        if 'denoise_strength' in settings:
            _camera_settings['denoise_strength'] = max(0, min(10, int(settings['denoise_strength'])))
        return _camera_settings.copy()

def reset_camera_settings() -> dict:
    """Reset camera settings to defaults from config."""
    with _settings_lock:
        _camera_settings['jpeg_quality'] = Config.JPEG_QUALITY
        _camera_settings['capture_scale'] = Config.CAPTURE_SCALE
        _camera_settings['denoise_strength'] = Config.DENOISE_STRENGTH
        return _camera_settings.copy()
