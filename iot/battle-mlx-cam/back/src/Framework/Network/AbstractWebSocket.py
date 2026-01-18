from abc import ABC, abstractmethod

class AbstractWebSocket(ABC):
    """Abstract base class for WebSocket clients."""

    @abstractmethod
    def connect(self, on_connect=None, on_disconnect=None):
        """Connect to the server."""
        pass

    @abstractmethod
    def send_image(self, image_base64: str, role: str, extra_data: dict = None) -> bool:
        """Send an image to the server."""
        pass

    @abstractmethod
    def close(self):
        """Close the connection."""
        pass
