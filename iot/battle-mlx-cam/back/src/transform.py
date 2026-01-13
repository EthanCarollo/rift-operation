"""Transform module - handles fal.ai Flux Kontext API calls."""

import os
import time
import base64
import requests
from PIL import Image
from io import BytesIO


# API Configuration
FAL_API_URL = "https://queue.fal.run/fal-ai/flux-kontext/dev"
# Persistent session for connection reuse
_session = requests.Session()


def get_api_key() -> str | None:
    """Get FAL_KEY from environment."""
    return os.getenv("FAL_KEY")


def transform_image(
    image_bytes: bytes,
    prompt: str,
    api_key: str | None = None
) -> tuple[bytes | None, float]:
    """
    Transform image using fal.ai Flux Kontext.
    
    Returns:
        Tuple of (transformed_image_bytes, elapsed_time)
    """
    start = time.time()
    
    key = api_key or get_api_key()
    if not key:
        raise ValueError("FAL_KEY not found in environment")
    
    # Compress input image (560x420 for speed)
    img = Image.open(BytesIO(image_bytes))
    img = img.resize((560, 420), Image.LANCZOS)
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=80)
    compressed = buffer.getvalue()
    
    # Convert to base64 data URI
    b64 = base64.b64encode(compressed).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{b64}"
    
    headers = {
        "Authorization": f"Key {key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "prompt": prompt,
        "image_url": data_uri,
        "num_inference_steps": 10,
        "guidance_scale": 2.5,
        "num_images": 1,
        "acceleration": "high",
    }
    
    # Log inference start
    prompt_preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
    print(f"[FLUX] 🚀 Starting inference | Prompt: \"{prompt_preview}\"")
    
    # Submit request
    response = _session.post(FAL_API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"[FLUX] ❌ API error {response.status_code}")
        raise RuntimeError(f"API error {response.status_code}: {response.text[:100]}")
    
    result = response.json()
    
    # Poll for completion if queued
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        if not status_url:
            raise RuntimeError("Missing status URL in response")
        
        while True:
            status_resp = _session.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status", "")
            
            if status == "COMPLETED":
                result = _session.get(response_url, headers=headers, timeout=60).json()
                break
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Transform failed: {status}")
            
            time.sleep(0.2)
    
    # Extract image from result
    if "images" not in result or len(result["images"]) == 0:
        raise RuntimeError("No images in response")
    
    image_url = result["images"][0].get("url", "")
    
    if image_url.startswith("data:"):
        _, data = image_url.split(",", 1)
        output_bytes = base64.b64decode(data)
    else:
        img_resp = _session.get(image_url, timeout=60)
        output_bytes = img_resp.content
    
    elapsed = time.time() - start
    print(f"[FLUX] ✅ Inference complete | Duration: {elapsed:.2f}s")
    
    return output_bytes, elapsed
