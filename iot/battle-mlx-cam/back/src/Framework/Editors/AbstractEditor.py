from abc import ABC, abstractmethod

class AbstractEditor(ABC):
    """Abstract base class for all image editors."""

    @abstractmethod
    def edit_image(self, image_bytes: bytes, prompt: str) -> tuple[bytes | None, float]:
        """
        Edit an image based on a prompt.
        
        Args:
            image_bytes: The input image data.
            prompt: The instruction for editing.
            
        Returns:
            A tuple containing:
                - The edited image bytes (or None if failed).
                - The time elapsed in seconds.
        """
        pass
