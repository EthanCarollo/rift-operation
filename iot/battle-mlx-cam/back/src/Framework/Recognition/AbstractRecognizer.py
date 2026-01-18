from abc import ABC, abstractmethod

class AbstractRecognizer(ABC):
    """Abstract base class for image recognition services."""

    @abstractmethod
    def predict(self, image_bytes: bytes) -> tuple[str, float]:
        """
        Predict the label of an image.
        
        Args:
            image_bytes: The input image data.
            
        Returns:
            A tuple containing:
                - The predicted label.
                - The confidence score or distance.
        """
        pass
