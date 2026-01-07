import os
import time
import base64
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import tempfile

# Load environment variables
load_dotenv()

# Configuration
FAL_API_KEY = os.getenv("FAL_KEY")
INPUT_IMAGE = "original.png"
MODEL = "schnell"  # "schnell" for fast (~4 steps), "dev" for quality (~20 steps)
STEPS = 4 if MODEL == "schnell" else 20
CONTROLNET_STRENGTH = 0.5
QUANTIZE = 8  # 8-bit quantization for faster inference


def load_image(filepath: str) -> tuple[bytes, float]:
    """Load image from file."""
    start_time = time.time()
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Image not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        image_bytes = f.read()
    
    elapsed = time.time() - start_time
    return image_bytes, elapsed


def transform_with_mflux(input_path: str, output_path: str, prompt: str) -> tuple[bytes, float]:
    """
    Transform image using mflux ControlNet locally on Mac with MLX.
    """
    start_time = time.time()
    
    # Build mflux command
    cmd = [
        "mflux-generate-controlnet",
        "--prompt", prompt,
        "--model", MODEL,
        "--steps", str(STEPS),
        "--seed", str(int(time.time()) % 1000000),
        "--height", "1024",
        "--width", "1024",
        "--quantize", str(QUANTIZE),
        "--controlnet-image-path", input_path,
        "--controlnet-strength", str(CONTROLNET_STRENGTH),
        "--output", output_path
    ]
    
    print(f"   Running: {' '.join(cmd[:6])}...")
    
    # Run mflux
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"mflux error: {result.stderr}")
    
    # Read the generated image
    with open(output_path, 'rb') as f:
        image_bytes = f.read()
    
    elapsed = time.time() - start_time
    return image_bytes, elapsed


def remove_background(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Remove background from image using fal.ai BiRefNet.
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
    
    payload = {
        "image_url": image_data_uri,
        "model": "General Use (Light)",
        "refine_foreground": True
    }
    
    # Submit request
    response = requests.post(
        "https://queue.fal.run/fal-ai/birefnet",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"fal.ai BiRefNet error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # Poll for result if needed
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        if not status_url or not response_url:
            raise RuntimeError(f"Missing status/response URLs: {result}")
        
        while True:
            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            
            status = status_data.get("status", "")
            if status == "COMPLETED":
                result_response = requests.get(response_url, headers=headers, timeout=60)
                result = result_response.json()
                break
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Background removal failed: {status}")
            else:
                time.sleep(0.3)
    
    # Extract image from response
    if "image" in result:
        image_url = result["image"].get("url", "")
        
        if image_url.startswith("data:"):
            _, data = image_url.split(",", 1)
            image_bytes = base64.b64decode(data)
        else:
            img_response = requests.get(image_url, timeout=60)
            if img_response.status_code != 200:
                raise RuntimeError(f"Failed to download result: {img_response.status_code}")
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
    filename = f"art_mlx_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    elapsed = time.time() - start_time
    return filepath, elapsed


def main():
    """Main function to run the image to art pipeline."""
    print("=" * 60)
    print("🎨 Image to Art - Local MLX (FLUX ControlNet)")
    print(f"   Model: {MODEL} | Steps: {STEPS} | Quantize: {QUANTIZE}-bit")
    print("=" * 60)
    
    timers = {}
    total_start = time.time()
    
    try:
        # Step 1: Load image
        print(f"\n📷 Loading image from {INPUT_IMAGE}...")
        original_image, load_time = load_image(INPUT_IMAGE)
        timers["Load Image"] = load_time
        print(f"   ✅ Image loaded ({len(original_image) / 1024:.1f} KB)")
        
        # Step 2: Transform with mflux ControlNet
        print("\n🎨 Transforming with FLUX ControlNet (MLX)...")
        prompt = "A hyperrealistic, highly detailed version of this image with photorealistic textures, professional lighting, and sharp details."
        
        # Create temp file for mflux output
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_output = tmp.name
        
        transformed_image, transform_time = transform_with_mflux(INPUT_IMAGE, temp_output, prompt)
        timers["FLUX ControlNet (MLX)"] = transform_time
        print(f"   ✅ Transformation complete ({len(transformed_image) / 1024:.1f} KB)")
        
        # Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        # Step 3: Remove background
        print("\n✂️  Removing background with BiRefNet...")
        final_image, rembg_time = remove_background(transformed_image)
        timers["Background Removal"] = rembg_time
        print(f"   ✅ Background removed ({len(final_image) / 1024:.1f} KB)")
        
        # Step 4: Save result
        print("\n💾 Saving result...")
        output_path, save_time = save_image(final_image)
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
