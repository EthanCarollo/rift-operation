from abc import ABC, abstractmethod

class AbstractCamera(ABC):
    """Abstract base class for camera devices."""

    @abstractmethod
    def open(self) -> bool:
        """Open camera connection."""
        pass

    @abstractmethod
    def close(self):
        """Close camera connection."""
        pass

    @abstractmethod
    def capture(self, settings: dict = None) -> bytes | None:
        """
        Capture a frame.
        
        Args:
            settings: Optional dictionary of settings (zoom, quality, etc).
            
        Returns:
            JPEG encoded bytes of the frame, or None if failed.
        """
        pass
