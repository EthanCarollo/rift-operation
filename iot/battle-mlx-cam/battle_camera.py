#!/usr/bin/env python3
"""
Battle Camera - Webcam capture with AI transformation and WebSocket streaming
Captures from webcam, transforms with Flux Kontext, removes background, sends via WebSocket
"""

import os
import sys
import cv2
import time
import json
import base64
import requests
import threading
import argparse
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# WebSocket
import websocket

# Load environment variables
load_dotenv()

# Configuration
FAL_API_KEY = os.getenv("FAL_KEY")
FAL_API_URL = "https://queue.fal.run/fal-ai/flux-kontext/dev"
WS_URL = "wss://server.riftoperation.ethan-folio.fr/ws"

# Persistent session for connection reuse
_session = requests.Session()

# WebSocket connection
_ws = None
_last_state = {}


def connect_websocket():
    """Connect to the Rift Operation WebSocket server."""
    global _ws
    
    def on_message(ws, message):
        global _last_state
        try:
            data = json.loads(message)
            _last_state = data
            state = data.get("battle_state", "unknown")
            print(f"   📡 WS: battle_state={state}")
        except json.JSONDecodeError:
            pass
    
    def on_error(ws, error):
        print(f"   ❌ WS Error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print(f"   🔌 WS Closed: {close_status_code}")
    
    def on_open(ws):
        print(f"   ✅ WS Connected to {WS_URL}")
    
    _ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run in background thread
    ws_thread = threading.Thread(target=_ws.run_forever, daemon=True)
    ws_thread.start()
    
    # Wait for connection
    time.sleep(1)
    return _ws


def send_image_ws(image_base64: str, role: str = "nightmare"):
    """Send transformed image via WebSocket."""
    global _ws, _last_state
    
    if _ws is None:
        print("   ⚠️  WebSocket not connected")
        return False
    
    try:
        payload = _last_state.copy()
        payload["device_id"] = "battle-camera-python"
        
        # Send as data URL
        data_url = f"data:image/png;base64,{image_base64}"
        
        if role == "dream":
            payload["battle_drawing_dream_image"] = data_url
            payload["battle_drawing_dream_recognised"] = True
        else:
            payload["battle_drawing_nightmare_image"] = data_url
            payload["battle_drawing_nightmare_recognised"] = True
        
        _ws.send(json.dumps(payload))
        print(f"   📤 Sent {role} image ({len(image_base64)//1024}KB)")
        return True
        
    except Exception as e:
        print(f"   ❌ Send failed: {e}")
        return False


def capture_webcam(camera_index: int = 0) -> bytes:
    """Capture a single frame from webcam and return as JPEG bytes."""
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {camera_index}")
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise RuntimeError("Failed to capture frame")
    
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    img = Image.fromarray(frame_rgb)
    
    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    return buffer.getvalue()


def transform_with_fal(image_bytes: bytes, prompt: str) -> tuple[bytes, float]:
    """Transform image using Flux Kontext via fal.ai."""
    start_time = time.time()
    
    if not FAL_API_KEY:
        raise ValueError("FAL_KEY not found in environment variables")
    
    # Compress for faster upload
    img = Image.open(BytesIO(image_bytes))
    img = img.resize((560, 420), Image.LANCZOS)
    
    compressed_buffer = BytesIO()
    img.save(compressed_buffer, format='JPEG', quality=85)
    compressed_bytes = compressed_buffer.getvalue()
    
    # Convert to base64 data URI
    image_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
    image_data_uri = f"data:image/jpeg;base64,{image_base64}"
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "prompt": prompt,
        "image_url": image_data_uri,
        "num_inference_steps": 10,
        "guidance_scale": 2.5,
        "num_images": 1,
        "acceleration": "high",
    }
    
    # Submit request
    response = _session.post(FAL_API_URL, headers=headers, json=payload, timeout=120)
    
    if response.status_code != 200:
        raise RuntimeError(f"fal.ai API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # Poll for result
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        if not status_url or not response_url:
            raise RuntimeError(f"Missing URLs in response: {result}")
        
        while True:
            status_response = _session.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            
            status = status_data.get("status", "")
            if status == "COMPLETED":
                result_response = _session.get(response_url, headers=headers, timeout=60)
                result = result_response.json()
                break
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Request failed: {status}")
            else:
                time.sleep(0.2)
    
    # Extract image
    if "images" in result and len(result["images"]) > 0:
        image_url = result["images"][0].get("url", "")
        
        if image_url.startswith("data:"):
            _, data = image_url.split(",", 1)
            image_bytes = base64.b64decode(data)
        else:
            img_response = _session.get(image_url, timeout=60)
            image_bytes = img_response.content
        
        return image_bytes, time.time() - start_time
    
    raise RuntimeError(f"No image in response: {result}")


def remove_background(image_bytes: bytes) -> tuple[bytes, float]:
    """Remove background using macOS Vision framework."""
    start_time = time.time()
    
    try:
        from Foundation import NSData
        from AppKit import NSImage, NSBitmapImageRep, NSPNGFileType
        from Quartz import (
            CGImageSourceCreateWithData, CGImageSourceCreateImageAtIndex,
            CIImage, CIContext, CIFilter, CIColor
        )
        from CoreFoundation import CFDataCreate, kCFAllocatorDefault
        import Vision
    except ImportError:
        raise RuntimeError("PyObjC not installed. Run: pip install pyobjc-framework-Vision pyobjc-framework-Quartz")
    
    # Load image
    cf_data = CFDataCreate(kCFAllocatorDefault, image_bytes, len(image_bytes))
    image_source = CGImageSourceCreateWithData(cf_data, None)
    cg_image = CGImageSourceCreateImageAtIndex(image_source, 0, None)
    
    if cg_image is None:
        raise RuntimeError("Failed to load image")
    
    # Create segmentation request
    request = Vision.VNGenerateForegroundInstanceMaskRequest.alloc().init()
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
    
    success, error = handler.performRequests_error_([request], None)
    if not success:
        raise RuntimeError(f"Vision request failed: {error}")
    
    results = request.results()
    if not results:
        raise RuntimeError("No foreground detected")
    
    observation = results[0]
    mask_buffer, error = observation.generateScaledMaskForImageForInstances_fromRequestHandler_error_(
        observation.allInstances(), handler, None
    )
    
    if error:
        raise RuntimeError(f"Failed to generate mask: {error}")
    
    # Apply mask
    mask_ci = CIImage.imageWithCVPixelBuffer_(mask_buffer)
    original_ci = CIImage.imageWithCGImage_(cg_image)
    extent = original_ci.extent()
    
    context = CIContext.context()
    blend_filter = CIFilter.filterWithName_("CIBlendWithMask")
    blend_filter.setValue_forKey_(original_ci, "inputImage")
    
    transparent = CIImage.imageWithColor_(CIColor.colorWithRed_green_blue_alpha_(0, 0, 0, 0))
    blend_filter.setValue_forKey_(transparent, "inputBackgroundImage")
    blend_filter.setValue_forKey_(mask_ci, "inputMaskImage")
    
    output_ci = blend_filter.valueForKey_("outputImage")
    output_cg = context.createCGImage_fromRect_(output_ci, extent)
    
    # Convert to PNG
    bitmap_rep = NSBitmapImageRep.alloc().initWithCGImage_(output_cg)
    png_data = bitmap_rep.representationUsingType_properties_(NSPNGFileType, None)
    
    return bytes(png_data), time.time() - start_time


def process_single(prompt: str, role: str = "nightmare", camera_index: int = 0):
    """Capture, transform, remove bg, send to WebSocket."""
    try:
        # 1. Capture
        print("📷 Capturing webcam...")
        image_bytes = capture_webcam(camera_index)
        print(f"   ✅ Captured ({len(image_bytes)//1024}KB)")
        
        # 2. Transform
        print(f"🎨 Transforming: {prompt[:50]}...")
        transformed, t_time = transform_with_fal(image_bytes, prompt)
        print(f"   ✅ Transformed in {t_time:.1f}s")
        
        # 3. Remove background
        print("✂️  Removing background...")
        final_image, bg_time = remove_background(transformed)
        print(f"   ✅ Background removed in {bg_time:.1f}s")
        
        # 4. Send via WebSocket
        image_b64 = base64.b64encode(final_image).decode('utf-8')
        send_image_ws(image_b64, role)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_loop(prompt: str, role: str = "nightmare", camera_index: int = 0, interval: float = 3.0):
    """Run continuous capture loop."""
    print("=" * 60)
    print("🎮 Battle Camera - Continuous Mode")
    print("=" * 60)
    print(f"   Role: {role.upper()}")
    print(f"   Camera: {camera_index}")
    print(f"   Prompt: {prompt}")
    print(f"   Interval: {interval}s")
    print("=" * 60)
    print("Press Ctrl+C to stop\n")
    
    # Connect WebSocket
    connect_websocket()
    time.sleep(1)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        start = time.time()
        success = process_single(prompt, role, camera_index)
        elapsed = time.time() - start
        
        if success:
            print(f"⏱️  Total: {elapsed:.1f}s")
        
        # Wait for next interval
        wait_time = max(0, interval - elapsed)
        if wait_time > 0:
            time.sleep(wait_time)


def main():
    parser = argparse.ArgumentParser(description="Battle Camera - Webcam to AI Art via WebSocket")
    parser.add_argument("--prompt", "-p", default="Steel katana sword in cartoon style", help="Transformation prompt")
    parser.add_argument("--role", "-r", choices=["dream", "nightmare"], default="nightmare", help="Agent role")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Camera index")
    parser.add_argument("--interval", "-i", type=float, default=3.0, help="Capture interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once instead of loop")
    
    args = parser.parse_args()
    
    if args.once:
        connect_websocket()
        time.sleep(1)
        process_single(args.prompt, args.role, args.camera)
    else:
        try:
            run_loop(args.prompt, args.role, args.camera, args.interval)
        except KeyboardInterrupt:
            print("\n\n👋 Stopped by user")


if __name__ == "__main__":
    main()
