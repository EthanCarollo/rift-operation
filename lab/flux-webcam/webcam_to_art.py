#!/usr/bin/env python3
"""
Webcam to Artistic Drawing using OpenRouter + Flux Max
Captures a photo from webcam, transforms it into a realistic drawing using Flux Max via OpenRouter.
"""

import os
import time
import base64
import requests
import cv2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OpenRouter chat completions endpoint (used for image generation)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def capture_webcam_photo() -> tuple[bytes, float]:
    """Capture a photo from the webcam and return the image bytes."""
    start_time = time.time()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")
    
    # Wait for camera to warm up
    time.sleep(0.5)
    
    # Capture frame
    ret, frame = cap.read()
    
    if not ret:
        cap.release()
        raise RuntimeError("Could not capture frame from webcam")
    
    # Release webcam
    cap.release()
    
    # Encode to JPEG
    _, buffer = cv2.imencode('.png', frame)
    image_bytes = buffer.tobytes()
    
    elapsed = time.time() - start_time
    return image_bytes, elapsed


def transform_with_flux_max(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Send image to OpenRouter Flux Max to transform into a realistic drawing.
    Uses the chat completions endpoint with image modality.
    Returns the transformed image bytes.
    """
    start_time = time.time()
    
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    # Encode image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/flux-webcam",
        "X-Title": "Flux Webcam Art"
    }
    
    # Use Flux 2 Max for image generation with chat completions format
    payload = {
        "model": "google/gemini-2.5-flash-image",
        "modalities": ["image", "text"],
        "messages": [
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
                        "text": "Transform this draw into a hyperrealistic digital image with transparent background (no background). Output as PNG with alpha transparency."
                    }
                ]
            }
        ]
    }
    
    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=180
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # Debug: print full response structure
    print(f"   📋 API Response keys: {result.keys()}")
    
    # Extract image from chat completions response
    # The image is in the assistant's message as a base64 data URL
    if "choices" in result and len(result["choices"]) > 0:
        message = result["choices"][0].get("message", {})
        print(f"   📋 Message keys: {message.keys()}")
        content = message.get("content", [])
        
        # Debug content type
        print(f"   📋 Content type: {type(content)}, length: {len(content) if isinstance(content, (list, str)) else 'N/A'}")
        
        # Handle string content (no image)
        if isinstance(content, str):
            if not content.strip():
                # Empty content - check for images elsewhere
                pass
            else:
                raise RuntimeError(f"No image in response, got text: {content[:200]}")
        
        # Look for image in content array
        if isinstance(content, list):
            for i, item in enumerate(content):
                print(f"   📋 Content item {i}: {type(item)}, keys: {item.keys() if isinstance(item, dict) else 'N/A'}")
                if isinstance(item, dict):
                    item_type = item.get("type", "")
                    # Check for image type
                    if item_type == "image_url":
                        image_url = item.get("image_url", {}).get("url", "")
                        if image_url.startswith("data:"):
                            # Extract base64 data
                            _, data = image_url.split(",", 1)
                            image_bytes = base64.b64decode(data)
                            elapsed = time.time() - start_time
                            return image_bytes, elapsed
                    # Check for image type directly
                    elif item_type == "image":
                        image_data = item.get("image", "") or item.get("data", "") or item.get("url", "")
                        if image_data.startswith("data:"):
                            _, data = image_data.split(",", 1)
                            image_bytes = base64.b64decode(data)
                            elapsed = time.time() - start_time
                            return image_bytes, elapsed
                        elif image_data:
                            # Could be raw base64 or URL
                            if image_data.startswith("http"):
                                img_response = requests.get(image_data, timeout=60)
                                image_bytes = img_response.content
                            else:
                                image_bytes = base64.b64decode(image_data)
                            elapsed = time.time() - start_time
                            return image_bytes, elapsed
        
        # Check for images array at message level
        images = message.get("images", [])
        print(f"   📋 Images array: {len(images)} items")
        if images:
            image_data = images[0]
            # Handle dict format: {"type": "image_url", "image_url": {"url": "data:..."}}
            if isinstance(image_data, dict):
                if image_data.get("type") == "image_url":
                    image_url = image_data.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:"):
                        _, data = image_url.split(",", 1)
                        image_bytes = base64.b64decode(data)
                        elapsed = time.time() - start_time
                        return image_bytes, elapsed
                    elif image_url.startswith("http"):
                        img_response = requests.get(image_url, timeout=60)
                        image_bytes = img_response.content
                        elapsed = time.time() - start_time
                        return image_bytes, elapsed
            # Handle string format
            elif isinstance(image_data, str):
                if image_data.startswith("data:"):
                    _, data = image_data.split(",", 1)
                    image_bytes = base64.b64decode(data)
                    elapsed = time.time() - start_time
                    return image_bytes, elapsed
                elif image_data.startswith("http"):
                    img_response = requests.get(image_data, timeout=60)
                    image_bytes = img_response.content
                    elapsed = time.time() - start_time
                    return image_bytes, elapsed
                else:
                    # Direct base64
                    image_bytes = base64.b64decode(image_data)
                    elapsed = time.time() - start_time
                    return image_bytes, elapsed
        
        # Print full result for debugging
        import json
        print(f"   📋 Full response:\n{json.dumps(result, indent=2)[:2000]}")
        
        raise RuntimeError(f"Could not find image in response")
    else:
        raise RuntimeError(f"Unexpected response format: {result}")


def save_image(image_bytes: bytes, output_dir: str = "output") -> tuple[str, float]:
    """Save the image bytes to a PNG file."""
    start_time = time.time()
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"drawing_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    # Write image
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    elapsed = time.time() - start_time
    return filepath, elapsed


def main():
    """Main function to run the webcam to art pipeline."""
    print("=" * 60)
    print("🎨 Webcam to Artistic Drawing - Flux Max via OpenRouter")
    print("=" * 60)
    
    timers = {}
    total_start = time.time()
    
    try:
        # Step 1: Capture photo from webcam
        print("\n📷 Capturing photo from webcam...")
        original_image, capture_time = capture_webcam_photo()
        timers["Webcam Capture"] = capture_time
        print(f"   ✅ Photo captured ({len(original_image) / 1024:.1f} KB)")
        
        # Save original image for reference
        os.makedirs("output", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_path = f"output/original_{timestamp}.jpg"
        with open(original_path, 'wb') as f:
            f.write(original_image)
        print(f"   💾 Original saved: {original_path}")
        
        # Step 2: Transform with Flux Max
        print("\n🎨 Transforming with Flux Max...")
        transformed_image, transform_time = transform_with_flux_max(original_image)
        timers["Flux Max API"] = transform_time
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
