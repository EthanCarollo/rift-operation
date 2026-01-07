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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
FAL_API_URL = "https://queue.fal.run/fal-ai/qwen-image-edit/image-to-image"
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


def enhance_prompt_with_ministral(image_bytes: bytes) -> tuple[str, float]:
    """
    Use Ministral via OpenRouter to analyze the image and generate an enhanced prompt.
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
    
    payload = {
        "model": "mistralai/ministral-3b-2512",
        "messages": [
            {
                "role": "system",
                "content": """You are an expert at crafting prompts for image-to-image AI models. 
Your task is to analyze a drawing/sketch and create a detailed prompt that will transform it into a hyperrealistic image.
Focus on:
- Identifying the main subject(s) in the drawing
- Describing textures, materials, and surfaces realistically
- Adding appropriate lighting and atmosphere
- Maintaining the original composition and intent

Output ONLY the prompt, no explanations. Keep it concise but descriptive (max 100 words)."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Analyze this drawing and create a prompt to transform it into a hyperrealistic image."
                    }
                ]
            }
        ],
        "max_tokens": 200
    }
    
    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    if "choices" in result and len(result["choices"]) > 0:
        enhanced_prompt = result["choices"][0]["message"]["content"].strip()
        elapsed = time.time() - start_time
        return enhanced_prompt, elapsed
    else:
        raise RuntimeError(f"Unexpected response format: {result}")


def transform_with_fal(image_bytes: bytes, prompt: str = "Transform this drawing into a hyperrealistic digital image.") -> tuple[bytes, float]:
    """
    Transform image using Flux Kontext via fal.ai.
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
    filename = f"art_fal_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    elapsed = time.time() - start_time
    return filepath, elapsed


def main():
    """Main function to run the image to art pipeline."""
    print("=" * 60)
    print("🎨 Image to Art - via fal.ai (Flux Kontext + BiRefNet)")
    print("=" * 60)
    
    timers = {}
    total_start = time.time()
    
    try:
        # Step 1: Load image
        print(f"\n📷 Loading image from {INPUT_IMAGE}...")
        original_image, load_time = load_image(INPUT_IMAGE)
        timers["Load Image"] = load_time
        print(f"   ✅ Image loaded ({len(original_image) / 1024:.1f} KB)")
        
        # Step 2: Enhance prompt with Ministral
        print("\n🧠 Enhancing prompt with Ministral...")
        enhanced_prompt, enhance_time = enhance_prompt_with_ministral(original_image)
        timers["Prompt Enhancement"] = enhance_time
        print(f"   ✅ Enhanced prompt:\n\n{enhanced_prompt}\n")
        
        # Step 3: Transform with Flux Kontext
        print("\n🎨 Transforming with Flux Kontext...")
        transformed_image, transform_time = transform_with_fal(original_image, enhanced_prompt)
        timers["Flux Kontext"] = transform_time
        print(f"   ✅ Transformation complete ({len(transformed_image) / 1024:.1f} KB)")
        
        # Step 4: Remove background
        print("\n✂️  Removing background with BiRefNet...")
        final_image, rembg_time = remove_background(transformed_image)
        timers["Background Removal"] = rembg_time
        print(f"   ✅ Background removed ({len(final_image) / 1024:.1f} KB)")
        
        # Step 5: Save result
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
