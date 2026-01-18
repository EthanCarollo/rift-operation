import os
import time
import base64
import requests
from io import BytesIO
from PIL import Image
from src.Framework.Editors.AbstractEditor import AbstractEditor

class FalFluxEditor(AbstractEditor):
    """
    Editor implementation using Fal.ai Flux models.
    """
    
    DEFAULT_MODEL = "fal-ai/flux-2/klein/4b/edit"

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.api_url = f"https://queue.fal.run/{model}"
        self._session = requests.Session()

    def _get_api_key(self) -> str | None:
        return os.getenv("FAL_KEY")

    def edit_image(self, image_bytes: bytes, prompt: str) -> tuple[bytes | None, float]:
        start = time.time()
        
        key = self._get_api_key()
        if not key:
            print("[FalFluxEditor] FAL_KEY not found in environment")
            return None, 0.0
        
        # Compress input image (560x420 for speed)
        try:
            img = Image.open(BytesIO(image_bytes))
            img = img.resize((560, 420), Image.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=80)
            compressed = buffer.getvalue()
        except Exception as e:
            print(f"[FalFluxEditor] Error processing image: {e}")
            return None, 0.0
        
        # Convert to base64 data URI
        b64 = base64.b64encode(compressed).decode('utf-8')
        data_uri = f"data:image/jpeg;base64,{b64}"
        
        headers = {
            "Authorization": f"Key {key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "prompt": prompt,
            "image_urls": [data_uri]
        }
        
        prompt_preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
        print(f"[FalFluxEditor] 🚀 Starting inference ({self.model}) | Prompt: \"{prompt_preview}\"")
        
        try:
            # Submit request
            response = self._session.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"[FalFluxEditor] ❌ API error {response.status_code}: {response.text[:100]}")
                return None, 0.0
            
            result = response.json()
            
            # Poll for completion if queued
            if result.get("status") == "IN_QUEUE" or "request_id" in result:
                status_url = result.get("status_url")
                response_url = result.get("response_url")
                
                if not status_url:
                    print("[FalFluxEditor] Missing status URL in response")
                    return None, 0.0
                
                while True:
                    status_resp = self._session.get(status_url, headers=headers, timeout=30)
                    status_data = status_resp.json()
                    status = status_data.get("status", "")
                    
                    if status == "COMPLETED":
                        result = self._session.get(response_url, headers=headers, timeout=60).json()
                        break
                    elif status in ["FAILED", "CANCELLED"]:
                        print(f"[FalFluxEditor] Transform failed: {status}")
                        return None, 0.0
                    
                    time.sleep(0.2)
            
            # Extract image from result
            if "images" not in result or len(result["images"]) == 0:
                print("[FalFluxEditor] No images in response")
                return None, 0.0
            
            image_url = result["images"][0].get("url", "")
            
            if image_url.startswith("data:"):
                _, data = image_url.split(",", 1)
                output_bytes = base64.b64decode(data)
            else:
                img_resp = self._session.get(image_url, timeout=60)
                output_bytes = img_resp.content
            
            elapsed = time.time() - start
            print(f"[FalFluxEditor] ✅ Inference complete | Duration: {elapsed:.2f}s")
            
            return output_bytes, elapsed

        except Exception as e:
            print(f"[FalFluxEditor] Exception during inference: {e}")
            return None, 0.0
