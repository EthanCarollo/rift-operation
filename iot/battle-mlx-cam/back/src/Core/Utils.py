import base64
from dataclasses import dataclass
from typing import Optional, Tuple

from .Config import Config
from . import FalFluxEditor, VisionBackgroundRemover, KNNRecognizer

@dataclass
class ProcessingResult:
    """Standardized result from the image processing pipeline."""
    label: str
    distance: float
    status_message: str
    is_valid_counter: bool = False
    prompt: Optional[str] = None
    output_image: Optional[bytes] = None
    should_skip: bool = False

class ImageProcessor:
    """
    Encapsulates Computer Vision and AI generation logic.
    Decouples business logic (BattleService) from image processing.
    """
    
    def __init__(self):
        self.knn = KNNRecognizer(dataset_name="default_dataset")
        self.editor = FalFluxEditor()
        self.bg_remover = VisionBackgroundRemover()
        
    def process_frame(self, image_bytes: bytes, current_attack: Optional[str] = None) -> ProcessingResult:
        
        # 0. Check Feature Flag
        if not Config.ENABLE_KNN:
            return ProcessingResult(
                label="DISABLED",
                distance=0.0,
                status_message="🚫 KNN Disabled (Config)",
                should_skip=True
            )

        try:
            # 1. KNN Recognition
            label, distance = self.knn.predict(image_bytes)
            
            # 2. Check for invalid labels (empty, etc.)
            if label in Config.PROMPT_MAPPING and Config.PROMPT_MAPPING[label] is None:
                 return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message=f"⚠️ {label.upper()}",
                    should_skip=True
                )
            
            # 3. Get Prompt
            prompt = Config.PROMPT_MAPPING.get(label, f"{label} in cartoon style")
            
            # 4. Validate Counter
            is_valid_counter = False
            if current_attack:
                required = Config.ATTACK_TO_COUNTER_LABEL.get(current_attack)
                is_valid_counter = (label == required)
            
            if not prompt:
                return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message=f"⚠️ Unrecognized: {label}",
                    should_skip=True
                )

            # 5. Transform Image (AI)
            # Pass original bytes; editor handles compression
            generated_bytes, _ = self.editor.edit_image(image_bytes, prompt)
            
            if not generated_bytes:
                 return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message="❌ Generation Failed",
                    prompt=prompt,
                    is_valid_counter=is_valid_counter,
                    should_skip=True
                )

            # 6. Remove Background
            final_bytes, _ = self.bg_remover.remove_background(generated_bytes)
            
            # Success
            return ProcessingResult(
                label=label,
                distance=distance,
                status_message=f"🧠 {label.upper()}",
                prompt=prompt,
                is_valid_counter=is_valid_counter,
                output_image=final_bytes,
                should_skip=False
            )

        except Exception as e:
            print(f"[ImageProcessor] Error: {e}")
            return ProcessingResult(
                label="ERROR",
                distance=0.0,
                status_message=f"❌ Error: {str(e)}",
                should_skip=True
            )
