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
        
        print(f"[ImageProcessor] 🔍 Starting processing (attack: {current_attack})")
        
        # 0. Check Feature Flag
        if not Config.ENABLE_KNN:
            print(f"[ImageProcessor] ❌ KNN DISABLED - Config.ENABLE_KNN is False")
            return ProcessingResult(
                label="DISABLED",
                distance=0.0,
                status_message="🚫 KNN Disabled (Config)",
                should_skip=True
            )

        try:
            # 1. KNN Recognition
            print(f"[ImageProcessor] 🧠 Calling KNN.predict()...")
            label, distance = self.knn.predict(image_bytes)
            print(f"[ImageProcessor] ✅ KNN Result: label='{label}', distance={distance:.2f}")
            
            if label == "Need Training":
                print(f"[ImageProcessor] ⚠️ KNN needs training data - skipping")
                return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message="⚠️ Need Training",
                    should_skip=True
                )
            
            # 2. Check for invalid labels (empty, etc.)
            if label in Config.PROMPT_MAPPING and Config.PROMPT_MAPPING[label] is None:
                print(f"[ImageProcessor] ⚠️ Label '{label}' has no prompt (skip generation)")
                return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message=f"⚠️ {label.upper()}",
                    should_skip=True
                )
            
            # 3. Get Prompt
            prompt = Config.PROMPT_MAPPING.get(label, f"{label} in cartoon style")
            print(f"[ImageProcessor] 📝 Prompt: '{prompt[:50]}...'")
            
            # 4. Validate Counter
            is_valid_counter = False
            if current_attack:
                required = Config.ATTACK_TO_COUNTER_LABEL.get(current_attack)
                is_valid_counter = (label == required)
                print(f"[ImageProcessor] 🎯 Counter check: attack='{current_attack}' requires='{required}', got='{label}', valid={is_valid_counter}")
            else:
                print(f"[ImageProcessor] ⚠️ No current_attack set - cannot validate counter")
            
            if not prompt:
                print(f"[ImageProcessor] ❌ No prompt for label '{label}' - skipping")
                return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message=f"⚠️ Unrecognized: {label}",
                    should_skip=True
                )

            # 5. Transform Image (AI)
            print(f"[ImageProcessor] 🎨 Generating image with AI...")
            generated_bytes, gen_time = self.editor.edit_image(image_bytes, prompt)
            
            if not generated_bytes:
                print(f"[ImageProcessor] ❌ AI generation failed")
                return ProcessingResult(
                    label=label,
                    distance=distance,
                    status_message="❌ Generation Failed",
                    prompt=prompt,
                    is_valid_counter=is_valid_counter,
                    should_skip=True
                )
            
            print(f"[ImageProcessor] ✅ AI generation complete ({gen_time:.2f}s)")

            # 6. Remove Background
            print(f"[ImageProcessor] 🖼️ Removing background...")
            final_bytes, bg_time = self.bg_remover.remove_background(generated_bytes)
            print(f"[ImageProcessor] ✅ Background removed ({bg_time:.2f}s)")
            
            # Success
            print(f"[ImageProcessor] 🎉 SUCCESS: label='{label}', valid_counter={is_valid_counter}")
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
            print(f"[ImageProcessor] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return ProcessingResult(
                label="ERROR",
                distance=0.0,
                status_message=f"❌ Error: {str(e)}",
                should_skip=True
            )
