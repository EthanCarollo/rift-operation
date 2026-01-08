#!/usr/bin/env python3
"""
Live Webcam to Cartoon Transformer
Uses Flux Kontext via fal.ai to transform webcam frames in real-time.
"""

import os
import time
import base64
import requests
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FAL_API_KEY = os.getenv("FAL_KEY")
FAL_API_URL = "https://queue.fal.run/fal-ai/flux-kontext/dev"
PROMPT = "Transform into cartoon style, vibrant colors, clean lines."
TRANSFORM_INTERVAL_MS = 2000

# Persistent session for connection reuse
_session = requests.Session()


def remove_background(image_bytes: bytes) -> bytes:
    """
    Remove background using macOS Vision framework (ultra-fast, local).
    """
    try:
        from Foundation import NSData
        from AppKit import NSBitmapImageRep, NSPNGFileType
        from Quartz import (
            CGImageSourceCreateWithData, CGImageSourceCreateImageAtIndex,
            CIImage, CIContext, CIFilter, CIColor
        )
        from CoreFoundation import CFDataCreate, kCFAllocatorDefault
        import Vision
    except ImportError:
        print("   ⚠️ PyObjC not installed, skipping bg removal")
        return image_bytes
    
    cf_data = CFDataCreate(kCFAllocatorDefault, image_bytes, len(image_bytes))
    image_source = CGImageSourceCreateWithData(cf_data, None)
    if not image_source:
        return image_bytes
    
    cg_image = CGImageSourceCreateImageAtIndex(image_source, 0, None)
    if not cg_image:
        return image_bytes
    
    request = Vision.VNGenerateForegroundInstanceMaskRequest.alloc().init()
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
    
    success, error = handler.performRequests_error_([request], None)
    if not success:
        return image_bytes
    
    results = request.results()
    if not results or len(results) == 0:
        return image_bytes
    
    observation = results[0]
    mask_buffer, error = observation.generateScaledMaskForImageForInstances_fromRequestHandler_error_(
        observation.allInstances(), handler, None
    )
    if error:
        return image_bytes
    
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
    
    bitmap_rep = NSBitmapImageRep.alloc().initWithCGImage_(output_cg)
    png_data = bitmap_rep.representationUsingType_properties_(NSPNGFileType, None)
    
    return bytes(png_data)


class WebcamCartoonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Live Webcam Cartoon Transformer")
        self.root.configure(bg="#1a1a2e")
        
        # State
        self.cap = None
        self.running = False
        self.last_frame_bytes = None
        self.transformed_image = None
        self.request_count = 0
        
        # Setup UI
        self.setup_ui()
        
        # Start webcam
        self.start_webcam()
        
        # Auto-start transformation after 1 second
        self.root.after(1000, self.start_transform)
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(
            main_frame, 
            text="🎨 Live Webcam Cartoon Transformer",
            font=("Helvetica", 18, "bold"),
            fg="#00d4ff",
            bg="#1a1a2e"
        )
        title.pack(pady=(0, 15))
        
        # Video frames container
        video_frame = tk.Frame(main_frame, bg="#1a1a2e")
        video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Original webcam
        left_frame = tk.Frame(video_frame, bg="#1a1a2e")
        left_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(left_frame, text="📹 Webcam", font=("Helvetica", 12), fg="white", bg="#1a1a2e").pack()
        self.webcam_label = tk.Label(left_frame, bg="#0f0f1a", width=320, height=240)
        self.webcam_label.pack(pady=5)
        
        # Transformed output
        right_frame = tk.Frame(video_frame, bg="#1a1a2e")
        right_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(right_frame, text="🎨 Cartoon", font=("Helvetica", 12), fg="white", bg="#1a1a2e").pack()
        self.cartoon_label = tk.Label(right_frame, bg="#0f0f1a", width=320, height=240)
        self.cartoon_label.pack(pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Starting webcam...")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Helvetica", 10),
            fg="#888",
            bg="#1a1a2e"
        )
        status_bar.pack(pady=10)
        
        # Controls
        controls = tk.Frame(main_frame, bg="#1a1a2e")
        controls.pack(pady=10)
        
        self.start_btn = ttk.Button(controls, text="▶️ Start Transform", command=self.start_transform)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(controls, text="⏹️ Stop", command=self.stop_transform, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Prompt entry
        prompt_frame = tk.Frame(main_frame, bg="#1a1a2e")
        prompt_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(prompt_frame, text="Prompt:", fg="white", bg="#1a1a2e").pack(side=tk.LEFT)
        self.prompt_var = tk.StringVar(value=PROMPT)
        prompt_entry = tk.Entry(prompt_frame, textvariable=self.prompt_var, width=50)
        prompt_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    def start_webcam(self):
        """Initialize webcam capture."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_var.set("❌ Failed to open webcam")
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.update_webcam()
    
    def update_webcam(self):
        """Update webcam preview."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize to 420p (560x420) for faster API processing
                frame_resized = cv2.resize(frame, (560, 420))
                
                # Encode as JPEG (smaller than PNG) with quality 80
                _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
                self.last_frame_bytes = buffer.tobytes()
                
                # Display in Tkinter
                img = Image.fromarray(frame_rgb)
                img = img.resize((320, 240))
                photo = ImageTk.PhotoImage(img)
                self.webcam_label.configure(image=photo)
                self.webcam_label.image = photo
        
        # Schedule next update
        self.root.after(33, self.update_webcam)  # ~30 FPS
    
    def start_transform(self):
        """Start the transformation loop."""
        if not FAL_API_KEY:
            self.status_var.set("❌ FAL_KEY not found in environment")
            return
        
        self.running = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_var.set("🔄 Transformation running...")
        self.transform_loop()
    
    def stop_transform(self):
        """Stop the transformation loop."""
        self.running = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_var.set("⏹️ Stopped")
    
    def transform_loop(self):
        """Main transformation loop - sends requests every 500ms regardless of pending results."""
        if not self.running:
            return
        
        if self.last_frame_bytes:
            # Run transformation in background thread (don't wait for previous)
            self.request_count += 1
            print(f"\n📤 Sending request #{self.request_count}...")
            thread = threading.Thread(target=self.do_transform, args=(self.request_count,), daemon=True)
            thread.start()
        
        # Schedule next transformation (every 500ms no matter what)
        self.root.after(TRANSFORM_INTERVAL_MS, self.transform_loop)
    
    def do_transform(self, request_id):
        """Perform the actual transformation (runs in background thread)."""
        try:
            start_time = time.time()
            print(f"   🔄 [#{request_id}] Starting transformation...")
            
            # Convert to base64 data URI
            image_base64 = base64.b64encode(self.last_frame_bytes).decode('utf-8')
            image_data_uri = f"data:image/jpeg;base64,{image_base64}"
            print(f"   📷 Frame size: {len(self.last_frame_bytes) / 1024:.1f} KB")
            
            headers = {
                "Authorization": f"Key {FAL_API_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "prompt": self.prompt_var.get(),
                "image_url": image_data_uri,
                "num_inference_steps": 10,
                "guidance_scale": 2.5,
                "num_images": 1,
                "acceleration": "high",
            }
            
            # Submit request
            print(f"   🚀 Sending to fal.ai...")
            response = _session.post(FAL_API_URL, headers=headers, json=payload, timeout=60)
            print(f"   📥 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ API error: {response.text[:200]}")
                raise RuntimeError(f"API error: {response.status_code}")
            
            result = response.json()
            
            # Poll for completion
            if result.get("status") == "IN_QUEUE" or "request_id" in result:
                status_url = result.get("status_url")
                response_url = result.get("response_url")
                print(f"   ⏳ Polling for result...")
                
                poll_count = 0
                while True:
                    status_response = _session.get(status_url, headers=headers, timeout=30)
                    status_data = status_response.json()
                    poll_count += 1
                    
                    if status_data.get("status") == "COMPLETED":
                        print(f"   ✅ Completed after {poll_count} polls")
                        result = _session.get(response_url, headers=headers, timeout=60).json()
                        break
                    elif status_data.get("status") in ["FAILED", "CANCELLED"]:
                        print(f"   ❌ Transform failed: {status_data}")
                        raise RuntimeError("Transform failed")
                    time.sleep(0.2)
            
            # Extract and display result
            if "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0].get("url", "")
                
                if image_url.startswith("data:"):
                    _, data = image_url.split(",", 1)
                    image_bytes = base64.b64decode(data)
                else:
                    img_response = _session.get(image_url, timeout=60)
                    image_bytes = img_response.content
                
                # Remove background (local, fast)
                print(f"   ✂️ [#{request_id}] Removing background...")
                bg_start = time.time()
                image_bytes = remove_background(image_bytes)
                print(f"   ✂️ [#{request_id}] Background removed in {time.time() - bg_start:.2f}s")
                
                # Update UI in main thread
                elapsed = time.time() - start_time
                print(f"   🎨 [#{request_id}] Image generated! Size: {len(image_bytes) / 1024:.1f} KB, Time: {elapsed:.2f}s")
                self.root.after(0, lambda: self.update_cartoon(image_bytes, elapsed))
        
        except Exception as e:
            print(f"   ❌ [#{request_id}] Error: {e}")
            self.root.after(0, lambda: self.status_var.set(f"❌ Error: {str(e)[:50]}"))
        
        finally:
            pass
    
    def update_cartoon(self, image_bytes, elapsed):
        """Update the cartoon display (runs in main thread)."""
        try:
            img = Image.open(BytesIO(image_bytes))
            img = img.resize((320, 240))
            photo = ImageTk.PhotoImage(img)
            self.cartoon_label.configure(image=photo)
            self.cartoon_label.image = photo
            self.status_var.set(f"✅ Transform: {elapsed:.2f}s")
        except Exception as e:
            self.status_var.set(f"❌ Display error: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        self.running = False
        if self.cap:
            self.cap.release()


def main():
    root = tk.Tk()
    root.geometry("800x600")
    root.resizable(True, True)
    
    app = WebcamCartoonApp(root)
    
    def on_close():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
