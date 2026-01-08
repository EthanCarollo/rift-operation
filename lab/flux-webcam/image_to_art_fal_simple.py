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

# Simple prompt - no LLM enhancement
PROMPT = """
A hyperrealistic, meticulously crafted steel katana sword with a gleaming, polished blade showcasing intricate Damascus steel patterns, etched engravings along the hilt, and a deep, reflective sheen under soft, diffused golden-hour lighting. The guard features delicate, hand-forged filigree with subtle oxidation highlights, while the pommel is intricately carved with a small, detailed dragon motif. The background is a softly blurred, misty forest at dawn, enhancing the sword’s majestic presence with natural, ambient reflections. Ultra-detailed textures, including fine grain of the steel, rivets, and worn edges, with lifelike reflections and a slight metallic patina.
"""


def load_image(filepath: str) -> tuple[bytes, float]:
    """Load image from file."""
    start_time = time.time()
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Image not found: {filepath}")
    
    with open(filepath, 'rb') as f:
        image_bytes = f.read()
    
    elapsed = time.time() - start_time
    return image_bytes, elapsed


def transform_with_fal(image_bytes: bytes, prompt: str) -> tuple[bytes, float]:
    """
    Transform image using Flux Kontext via fal.ai.
    """
    start_time = time.time()
    
    if not FAL_API_KEY:
        raise ValueError("FAL_KEY not found in environment variables")
    
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_data_uri = f"data:image/png;base64,{image_base64}"
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    
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
    
    response = requests.post(FAL_API_URL, headers=headers, json=payload, timeout=120)
    
    if response.status_code != 200:
        raise RuntimeError(f"fal.ai API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # Poll for result
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        while True:
            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            
            if status_data.get("status") == "COMPLETED":
                result = requests.get(response_url, headers=headers, timeout=60).json()
                break
            elif status_data.get("status") in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Request failed: {status_data}")
            time.sleep(0.5)
    
    # Extract image
    if "images" in result and len(result["images"]) > 0:
        image_url = result["images"][0].get("url", "")
        
        if image_url.startswith("data:"):
            _, data = image_url.split(",", 1)
            image_bytes = base64.b64decode(data)
        else:
            image_bytes = requests.get(image_url, timeout=60).content
        
        return image_bytes, time.time() - start_time
    
    raise RuntimeError(f"No image in response: {result}")


def remove_background(image_bytes: bytes) -> tuple[bytes, float]:
    """Remove background using fal.ai BiRefNet."""
    start_time = time.time()
    
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "image_url": f"data:image/png;base64,{image_base64}",
        "model": "General Use (Light)",
        "refine_foreground": True
    }
    
    response = requests.post(
        "https://queue.fal.run/fal-ai/birefnet",
        headers=headers, json=payload, timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"fal.ai BiRefNet error: {response.status_code}")
    
    result = response.json()
    
    # Poll for result
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        while True:
            status_data = requests.get(status_url, headers=headers, timeout=30).json()
            
            if status_data.get("status") == "COMPLETED":
                result = requests.get(response_url, headers=headers, timeout=60).json()
                break
            elif status_data.get("status") in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Background removal failed")
            time.sleep(0.3)
    
    # Extract image
    if "image" in result:
        image_url = result["image"].get("url", "")
        
        if image_url.startswith("data:"):
            _, data = image_url.split(",", 1)
            image_bytes = base64.b64decode(data)
        else:
            image_bytes = requests.get(image_url, timeout=60).content
        
        return image_bytes, time.time() - start_time
    
    raise RuntimeError(f"No image in response: {result}")


def save_image(image_bytes: bytes, output_dir: str = "output", suffix: str = "") -> tuple[str, float]:
    """Save the image to a PNG file."""
    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"art_simple_{timestamp}{suffix}.png")
    
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    return filepath, time.time() - start_time


def main():
    """Main pipeline - no prompt enhancement."""
    print("=" * 60)
    print("🎨 Image to Art - Simple (No Prompt Enhancement)")
    print("=" * 60)
    
    timers = {}
    total_start = time.time()
    
    try:
        # Step 1: Load
        print(f"\n📷 Loading {INPUT_IMAGE}...")
        image, load_time = load_image(INPUT_IMAGE)
        timers["Load"] = load_time
        print(f"   ✅ Loaded ({len(image) / 1024:.1f} KB)")
        
        # Step 2: Transform
        print(f"\n🎨 Transforming...")
        print(f"   Prompt: \"{PROMPT[:60]}...\"")
        transformed, transform_time = transform_with_fal(image, PROMPT)
        timers["Transform"] = transform_time
        print(f"   ✅ Done ({len(transformed) / 1024:.1f} KB)")
        
        # Step 3: Save WITH background
        print("\n💾 Saving (with background)...")
        path_with_bg, save_time1 = save_image(transformed, suffix="_with_bg")
        timers["Save (with BG)"] = save_time1
        print(f"   ✅ Saved: {path_with_bg}")
        
        # Step 4: Remove background
        print("\n✂️  Removing background...")
        final, rembg_time = remove_background(transformed)
        timers["Remove BG"] = rembg_time
        print(f"   ✅ Done ({len(final) / 1024:.1f} KB)")
        
        # Step 5: Save WITHOUT background
        print("\n💾 Saving (transparent)...")
        path_no_bg, save_time2 = save_image(final, suffix="_no_bg")
        timers["Save (no BG)"] = save_time2
        print(f"   ✅ Saved: {path_no_bg}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        timers["Error"] = time.time() - total_start
    
    timers["Total"] = time.time() - total_start
    
    print("\n" + "=" * 60)
    print("⏱️  TIMING")
    print("=" * 60)
    for step, t in timers.items():
        print(f"   {step:.<30} {t:>6.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
