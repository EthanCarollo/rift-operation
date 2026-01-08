import os
import time
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables

model_id = "google/gemini-2.5-flash-image"
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
INPUT_IMAGE = "original.png"


def load_image(filepath: str) -> tuple[bytes, float]:
    """Load image from file."""
    start_time = time.time()
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Image not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        image_bytes = f.read()
    
    elapsed = time.time() - start_time
    return image_bytes, elapsed


def transform_with_flux(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Transform image using Flux Schnell (fastest model) via OpenRouter.
    """
    start_time = time.time()
    
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/flux-webcam",
        "X-Title": "Flux Image Art"
    }
    
    # Use Flux Schnell - the fastest model
    payload = {
        "model": model_id,
        "modalities": ["image", "text"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Transform this draw into a hyperrealistic digital image."
                    }
                ]
            }
        ]
    }
    
    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # Extract image from response
    if "choices" in result and len(result["choices"]) > 0:
        message = result["choices"][0].get("message", {})
        images = message.get("images", [])
        
        if images:
            image_data = images[0]
            if isinstance(image_data, dict) and image_data.get("type") == "image_url":
                image_url = image_data.get("image_url", {}).get("url", "")
                if image_url.startswith("data:"):
                    _, data = image_url.split(",", 1)
                    image_bytes = base64.b64decode(data)
                    elapsed = time.time() - start_time
                    return image_bytes, elapsed
        
        raise RuntimeError(f"Could not find image in response: {result}")
    else:
        raise RuntimeError(f"Unexpected response format: {result}")


def save_image(image_bytes: bytes, output_dir: str = "output") -> tuple[str, float]:
    """Save the image bytes to a PNG file."""
    start_time = time.time()
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"art_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    elapsed = time.time() - start_time
    return filepath, elapsed


def main():
    """Main function to run the image to art pipeline."""
    print("=" * 60)
    print("🎨 Image to Art - via OpenRouter  : " + model_id)
    print("=" * 60)
    
    timers = {}
    total_start = time.time()
    
    try:
        # Step 1: Load image
        print(f"\n📷 Loading image from {INPUT_IMAGE}...")
        original_image, load_time = load_image(INPUT_IMAGE)
        timers["Load Image"] = load_time
        print(f"   ✅ Image loaded ({len(original_image) / 1024:.1f} KB)")
        
        # Step 2: Transform with Flux Schnell
        print("\n🎨 Transforming with " + model_id)
        transformed_image, transform_time = transform_with_flux(original_image)
        timers[model_id] = transform_time
        print(f"   ✅ Transformation complete ({len(transformed_image) / 1024:.1f} KB)")
        
        # Step 3: Save result
        print("\n💾 Saving result...")
        output_path, save_time = save_image(transformed_image)
        timers["Save Image"] = save_time
        print(f"   ✅ Saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        timers["Error occurred at"] = time.time() - total_start
    
    # Calculate total time
    timers["Total"] = time.time() - total_start
    
    # Print all timers
    print("\n" + "=" * 60)
    print("⏱️  TIMING SUMMARY")
    print("=" * 60)
    for step, duration in timers.items():
        print(f"   {step:.<40} {duration:>8.2f}s")
    print("=" * 60)
    
    return timers


if __name__ == "__main__":
    main()
