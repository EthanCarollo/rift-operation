import os
import time
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FAL_API_KEY = os.getenv("FAL_KEY")
FAL_API_URL = "https://queue.fal.run/fal-ai/flux-kontext/dev"
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


def transform_with_fal(image_bytes: bytes, prompt: str = "Transform this drawing into a hyperrealistic digital image.") -> tuple[bytes, float]:
    """
    Transform image using Flux Kontext via fal.ai.
    Uses image_bytes directly (converted to base64 data URI).
    """
    start_time = time.time()
    
    if not FAL_API_KEY:
        raise ValueError("FAL_KEY not found in environment variables")
    
    # Convert image to base64 data URI
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_data_uri = f"data:image/png;base64,{image_base64}"
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Payload for fal.ai flux-kontext/dev
    payload = {
        "prompt": prompt,
        "image_url": image_data_uri,
        "num_inference_steps": 28,
        "guidance_scale": 2.5,
        "num_images": 1,
        "output_format": "png",
        "acceleration": "regular",
        "resolution_mode": "match_input"
    }
    
    # Submit request to queue
    response = requests.post(
        FAL_API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"fal.ai API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # Poll for result using URLs from response
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        if not status_url or not response_url:
            raise RuntimeError(f"Missing status/response URLs in response: {result}")
        
        # Poll for completion
        while True:
            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            
            status = status_data.get("status", "")
            if status == "COMPLETED":
                # Get the result
                result_response = requests.get(response_url, headers=headers, timeout=60)
                result = result_response.json()
                break
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Request failed with status: {status} - {status_data}")
            else:
                # Still processing (IN_QUEUE or IN_PROGRESS), wait a bit
                time.sleep(0.5)
    
    # Extract image from response
    if "images" in result and len(result["images"]) > 0:
        image_info = result["images"][0]
        image_url = image_info.get("url", "")
        
        if image_url.startswith("data:"):
            # Data URI
            _, data = image_url.split(",", 1)
            image_bytes = base64.b64decode(data)
        else:
            # Regular URL - download it
            img_response = requests.get(image_url, timeout=60)
            if img_response.status_code != 200:
                raise RuntimeError(f"Failed to download result image: {img_response.status_code}")
            image_bytes = img_response.content
        
        elapsed = time.time() - start_time
        return image_bytes, elapsed
    else:
        raise RuntimeError(f"Could not find image in response: {result}")


def save_image(image_bytes: bytes, output_dir: str = "output") -> tuple[str, float]:
    """Save the image bytes to a PNG file."""
    start_time = time.time()
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kontext_dev_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    elapsed = time.time() - start_time
    return filepath, elapsed


def main(prompt: str = "Transform this image into art."):
    """Main function to run the Flux Kontext image transformation."""
    print("=" * 60)
    print("🎨 Flux Kontext Dev - Image Transformation")
    print("=" * 60)
    
    timers = {}
    total_start = time.time()
    
    try:
        # Step 1: Load image
        print(f"\n📷 Loading image from {INPUT_IMAGE}...")
        original_image, load_time = load_image(INPUT_IMAGE)
        timers["Load Image"] = load_time
        print(f"   ✅ Image loaded ({len(original_image) / 1024:.1f} KB)")
        
        # Step 2: Transform with Flux Kontext
        print(f"\n🎨 Transforming with Flux Kontext Dev...")
        print(f"   Prompt: {prompt}")
        transformed_image, transform_time = transform_with_fal(original_image, prompt)
        timers["Flux Kontext"] = transform_time
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
    import sys
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Transform this image into art."
    main(prompt)
