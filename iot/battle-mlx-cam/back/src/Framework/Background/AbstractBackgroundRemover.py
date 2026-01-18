from abc import ABC, abstractmethod

class AbstractBackgroundRemover(ABC):
    """Abstract base class for background removal services."""

    @abstractmethod
    def remove_background(self, image_bytes: bytes) -> tuple[bytes, float]:
        """
        Remove background from an image.
        
        Args:
            image_bytes: The input image data.
            
        Returns:
            A tuple containing:
                - The image bytes with transparency.
                - The time elapsed in seconds.
        """
        pass
