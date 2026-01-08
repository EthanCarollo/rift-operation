import os
import asyncio
import fal_client
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import io
from PIL import Image
import torch
import torchvision.transforms as T
import numpy as np
from transformers import AutoModelForImageSegmentation

# Load environment variables
load_dotenv()

# Configuration
INPUT_IMAGE = "original.png"
WORKFLOW_ID = "workflows/EthanCarollo/rift-operation-workflow"

# The prompt based on user's preference
PROMPT = """
steel katana sword in a cartoon style.
"""

# Global variables for the background removal to avoid reloading
_rembg_model = None

def get_rembg_model():
    global _rembg_model
    if _rembg_model is None:
        print("\n🧠 Loading local BiRefNet model (this may take a moment)...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        model_id = "ZhengPeng7/BiRefNet"
        
        # Load model with trust_remote_code=True
        _rembg_model = AutoModelForImageSegmentation.from_pretrained(model_id, trust_remote_code=True)
        _rembg_model.to(device)
        _rembg_model.eval()
        
    return _rembg_model

async def remove_background_local(image_bytes: bytes) -> tuple[bytes, float]:
    """
    Remove background locally using BiRefNet with manual preprocessing.
    """
    start_time = time.time()
    
    # Load model
    model = get_rembg_model()
    device = next(model.parameters()).device
    
    # Load image
    input_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    original_size = input_image.size
    
    # Preprocess (Standard BiRefNet: 1024x1024, normalized)
    transform_image = T.Compose([
        T.Resize((1024, 1024)),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    input_tensor = transform_image(input_image).unsqueeze(0).to(device)
    
    # Inference
    print("   ✂️  Processing background removal locally (MPS)...")
    with torch.no_grad():
        preds = model(input_tensor)[-1].sigmoid().cpu()
    
    # Post-process mask
    mask = preds[0].squeeze().numpy()
    mask_img = Image.fromarray((mask * 255).astype(np.uint8)).resize(original_size, Image.BILINEAR)
    
    # Apply mask to original image to create transparent PNG
    rgba_image = input_image.copy().convert("RGBA")
    rgba_image.putalpha(mask_img)
    
    # Convert PIL Image back to bytes
    output_buffer = io.BytesIO()
    rgba_image.save(output_buffer, format="PNG")
    output_bytes = output_buffer.getvalue()
    
    elapsed = time.time() - start_time
    return output_bytes, elapsed

async def run_workflow():
    if not os.path.exists(INPUT_IMAGE):
        print(f"❌ Error: {INPUT_IMAGE} not found")
        return

    print("=" * 60)
    print(f"🚀 Running Fal.ai Workflow: {WORKFLOW_ID}")
    print("=" * 60)

    start_time = time.time()
    
    # Step 1: Upload image
    print(f"\n📷 Uploading {INPUT_IMAGE} to fal.ai...")
    upload_start = time.time()
    image_url = fal_client.upload_file(INPUT_IMAGE)
    upload_time = time.time() - upload_start
    print(f"   ✅ Uploaded in {upload_time:.2f}s! URL: {image_url}")

    # Step 2: Execute Workflow
    print(f"\n🔄 Executing workflow...")
    workflow_start = time.time()
    
    stream = fal_client.stream_async(
        WORKFLOW_ID,
        arguments={
            "prompt": PROMPT,
            "image_url_field": image_url
        },
    )
    
    result = None
    async for event in stream:
        if isinstance(event, fal_client.InProgress):
            if event.logs:
                for log in event.logs:
                    print(f"   [fal.ai] {log['message']}")
        else:
            result = event
    
    workflow_time = time.time() - workflow_start
    if not result:
        raise RuntimeError("Workflow finished without a result")
        
    print(f"   ✅ Workflow complete in {workflow_time:.2f}s!")

    # Step 3: Parse and Save Results
    print("\n💾 Processing and saving results...")
    save_start = time.time()
    
    payload = result
    if isinstance(result, dict) and result.get("type") == "output" and "output" in result:
        payload = result["output"]
    
    images_to_save = []
    if "images" in payload:
        images_to_save = payload["images"]
    elif "image" in payload:
        images_to_save = [payload["image"]]
    
    if not images_to_save:
        print("   ⚠️ No images found in result!")
        print(f"   Full result: {result}")
    else:
        os.makedirs("output", exist_ok=True)
        for i, img in enumerate(images_to_save):
            img_url = img.get("url")
            if not img_url:
                continue
                
            response = requests.get(img_url)
            if response.status_code == 200:
                image_bytes = response.content
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save WITH background
                filename_bg = f"output/workflow_{timestamp}_{i}_with_bg.png"
                with open(filename_bg, "wb") as f:
                    f.write(image_bytes)
                print(f"   ✅ Saved (with background) to: {filename_bg}")
                
                # Remove background LOCALLY
                try:
                    no_bg_bytes, rembg_time = await remove_background_local(image_bytes)
                    
                    # Save WITHOUT background
                    filename_nobg = f"output/workflow_{timestamp}_{i}_no_bg.png"
                    with open(filename_nobg, "wb") as f:
                        f.write(no_bg_bytes)
                    print(f"   ✅ Saved (transparent) to: {filename_nobg} (Local BiRefNet: {rembg_time:.2f}s)")
                except Exception as e:
                    print(f"   ❌ Failed to remove background locally: {e}")
            else:
                print(f"   ❌ Failed to download result {i+1}: {img_url}")
    
    save_time = time.time() - save_start
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("⏱️  TIMING SUMMARY")
    print("=" * 60)
    print(f"   Upload Image............................ {upload_time:>8.2f}s")
    print(f"   Workflow Execution...................... {workflow_time:>8.2f}s")
    print(f"   Save & Local Processing................. {save_time:>8.2f}s")
    print("-" * 60)
    print(f"   Total................................... {total_time:>8.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_workflow())
