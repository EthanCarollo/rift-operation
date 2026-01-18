from abc import ABC, abstractmethod

class AbstractWebServer(ABC):
    """Abstract base class for Web Servers."""

    @abstractmethod
    def start(self, host: str, port: int):
        """Start the web server."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the web server."""
        pass
