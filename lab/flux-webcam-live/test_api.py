#!/usr/bin/env python3
"""
Test script to verify webcam and fal.ai API work correctly.
Run this to debug issues before using the full UI app.
"""

import os
import time
import base64
import requests
import cv2
from dotenv import load_dotenv

load_dotenv()

FAL_API_KEY = os.getenv("FAL_KEY")
FAL_API_URL = "https://queue.fal.run/fal-ai/flux-kontext/dev"
_session = requests.Session()


def test_webcam():
    """Test 1: Verify webcam works."""
    print("\n" + "=" * 50)
    print("TEST 1: Webcam Capture")
    print("=" * 50)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ FAILED: Could not open webcam")
        return None
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ FAILED: Could not read frame")
        return None
    
    # Convert to PNG bytes
    _, buffer = cv2.imencode('.png', frame)
    image_bytes = buffer.tobytes()
    
    print(f"✅ PASSED: Captured frame {frame.shape}")
    print(f"   PNG size: {len(image_bytes) / 1024:.1f} KB")
    
    return image_bytes


def test_api_key():
    """Test 2: Verify FAL_KEY is set."""
    print("\n" + "=" * 50)
    print("TEST 2: API Key")
    print("=" * 50)
    
    if not FAL_API_KEY:
        print("❌ FAILED: FAL_KEY not found in environment")
        print("   Set it in .env file: FAL_KEY=your_key_here")
        return False
    
    print(f"✅ PASSED: FAL_KEY found ({FAL_API_KEY[:10]}...)")
    return True


def test_transform(image_bytes):
    """Test 3: Verify fal.ai transformation."""
    print("\n" + "=" * 50)
    print("TEST 3: Fal.ai Transformation")
    print("=" * 50)
    
    if not image_bytes:
        print("⚠️ SKIPPED: No image bytes provided")
        return False
    
    if not FAL_API_KEY:
        print("⚠️ SKIPPED: No API key")
        return False
    
    start_time = time.time()
    
    # Convert to base64 data URI
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_data_uri = f"data:image/png;base64,{image_base64}"
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "prompt": "Transform into cartoon style.",
        "image_url": image_data_uri,
        "num_inference_steps": 10,
        "guidance_scale": 2.5,
        "num_images": 1,
        "acceleration": "high",
    }
    
    print("   🚀 Sending request...")
    try:
        response = _session.post(FAL_API_URL, headers=headers, json=payload, timeout=60)
        print(f"   📥 Response: {response.status_code}")
    except Exception as e:
        print(f"❌ FAILED: Request error: {e}")
        return False
    
    if response.status_code != 200:
        print(f"❌ FAILED: API error: {response.text[:200]}")
        return False
    
    result = response.json()
    print(f"   📋 Result keys: {list(result.keys())}")
    
    # Poll for completion
    if result.get("status") == "IN_QUEUE" or "request_id" in result:
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        
        if not status_url or not response_url:
            print(f"❌ FAILED: Missing URLs in response")
            return False
        
        print("   ⏳ Polling...")
        poll_count = 0
        while True:
            status_response = _session.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()
            poll_count += 1
            
            status = status_data.get("status", "")
            print(f"   📊 Poll {poll_count}: {status}")
            
            if status == "COMPLETED":
                result = _session.get(response_url, headers=headers, timeout=60).json()
                break
            elif status in ["FAILED", "CANCELLED"]:
                print(f"❌ FAILED: Transform failed: {status_data}")
                return False
            
            time.sleep(0.5)
    
    # Extract image
    if "images" in result and len(result["images"]) > 0:
        image_url = result["images"][0].get("url", "")
        
        if image_url.startswith("data:"):
            _, data = image_url.split(",", 1)
            output_bytes = base64.b64decode(data)
        else:
            img_response = _session.get(image_url, timeout=60)
            output_bytes = img_response.content
        
        elapsed = time.time() - start_time
        print(f"✅ PASSED: Generated image ({len(output_bytes) / 1024:.1f} KB) in {elapsed:.2f}s")
        
        # Save test output
        with open("test_output.png", "wb") as f:
            f.write(output_bytes)
        print(f"   💾 Saved to: test_output.png")
        
        return True
    else:
        print(f"❌ FAILED: No images in result: {result}")
        return False


def main():
    print("\n🔧 WEBCAM CARTOON TRANSFORMER - TEST SUITE")
    print("=" * 50)
    
    # Run tests
    image_bytes = test_webcam()
    api_ok = test_api_key()
    
    if image_bytes and api_ok:
        test_transform(image_bytes)
    
    print("\n" + "=" * 50)
    print("TESTS COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
