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

# Persistent session for connection reuse (faster)
_session = requests.Session()


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
    
    # Compress image for faster upload (resize to 420p, JPEG quality 85)
    from PIL import Image
    from io import BytesIO
    
    img = Image.open(BytesIO(image_bytes))
    img = img.resize((560, 420), Image.LANCZOS)
    
    compressed_buffer = BytesIO()
    img.save(compressed_buffer, format='JPEG', quality=85)
    compressed_bytes = compressed_buffer.getvalue()
    
    print(f"   📦 Compressed: {len(image_bytes)/1024:.1f}KB → {len(compressed_bytes)/1024:.1f}KB")
    
    # Convert compressed image to base64 data URI
    image_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
    image_data_uri = f"data:image/jpeg;base64,{image_base64}"
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Payload for fal.ai flux-kontext/dev
    payload = {
        "prompt": prompt,
        "image_url": image_data_uri,
        "num_inference_steps": 10,
        "guidance_scale": 2.5,
        "num_images": 1,
        "acceleration": "high",
    }
    
    # Submit request to queue
    response = _session.post(
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
            status_response = _session.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            
            status = status_data.get("status", "")
            if status == "COMPLETED":
                # Get the result
                result_response = _session.get(response_url, headers=headers, timeout=60)
                result = result_response.json()
                break
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Request failed with status: {status} - {status_data}")
            else:
                # Still processing (IN_QUEUE or IN_PROGRESS), wait a bit
                time.sleep(0.2)
    
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
            img_response = _session.get(image_url, timeout=60)
            if img_response.status_code != 200:
                raise RuntimeError(f"Failed to download result image: {img_response.status_code}")
            image_bytes = img_response.content
        
        elapsed = time.time() - start_time
        return image_bytes, elapsed
    else:
        raise RuntimeError(f"Could not find image in response: {result}")


def remove_background(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Remove background using macOS Vision framework (ultra-fast, local).
    Uses VNGenerateForegroundInstanceMaskRequest for subject isolation.
    """
    start_time = time.time()
    
    try:
        # Import macOS frameworks via PyObjC
        from Foundation import NSData
        from AppKit import NSImage, NSBitmapImageRep, NSPNGFileType
        from Quartz import (
            CGImageSourceCreateWithData, CGImageSourceCreateImageAtIndex,
            CIImage, CIContext, CIFilter, kCGImagePropertyOrientation
        )
        from CoreFoundation import CFDataCreate, kCFAllocatorDefault
        import Vision
        import objc
    except ImportError:
        raise RuntimeError("PyObjC not installed. Run: pip install pyobjc-framework-Vision pyobjc-framework-Quartz")
    
    # Load image via CGImageSource (more reliable)
    cf_data = CFDataCreate(kCFAllocatorDefault, image_bytes, len(image_bytes))
    image_source = CGImageSourceCreateWithData(cf_data, None)
    if image_source is None:
        raise RuntimeError("Failed to create image source")
    
    cg_image = CGImageSourceCreateImageAtIndex(image_source, 0, None)
    if cg_image is None:
        raise RuntimeError("Failed to load CGImage")
    
    # Create segmentation request
    request = Vision.VNGenerateForegroundInstanceMaskRequest.alloc().init()
    
    # Create request handler with CGImage
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
    
    # Perform request
    success, error = handler.performRequests_error_([request], None)
    if not success:
        raise RuntimeError(f"Vision request failed: {error}")
    
    results = request.results()
    if not results or len(results) == 0:
        raise RuntimeError("No foreground detected in image")
    
    # Get the mask observation
    observation = results[0]
    
    # Generate mask as CVPixelBuffer
    mask_buffer, error = observation.generateScaledMaskForImageForInstances_fromRequestHandler_error_(
        observation.allInstances(), handler, None
    )
    if error:
        raise RuntimeError(f"Failed to generate mask: {error}")
    
    # Convert mask to CIImage
    mask_ci = CIImage.imageWithCVPixelBuffer_(mask_buffer)
    
    # Load original as CIImage
    original_ci = CIImage.imageWithCGImage_(cg_image)
    extent = original_ci.extent()
    
    # Use CIBlendWithMask filter
    context = CIContext.context()
    
    blend_filter = CIFilter.filterWithName_("CIBlendWithMask")
    blend_filter.setValue_forKey_(original_ci, "inputImage")
    
    # Create transparent background
    from Quartz import CIColor
    transparent = CIImage.imageWithColor_(CIColor.colorWithRed_green_blue_alpha_(0, 0, 0, 0))
    blend_filter.setValue_forKey_(transparent, "inputBackgroundImage")
    blend_filter.setValue_forKey_(mask_ci, "inputMaskImage")
    
    output_ci = blend_filter.valueForKey_("outputImage")
    
    # Render to CGImage
    output_cg = context.createCGImage_fromRect_(output_ci, extent)
    
    # Convert to PNG bytes
    bitmap_rep = NSBitmapImageRep.alloc().initWithCGImage_(output_cg)
    png_data = bitmap_rep.representationUsingType_properties_(NSPNGFileType, None)
    
    output_bytes = bytes(png_data)
    elapsed = time.time() - start_time
    return output_bytes, elapsed


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


def main(prompt: str = "Steel katana sword in a cartoon style."):
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
        
        # Step 3: Remove background with BiRefNet
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
