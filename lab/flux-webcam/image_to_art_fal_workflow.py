import os
import asyncio
import base64
import fal_client
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
INPUT_IMAGE = "original.png"
WORKFLOW_ID = "workflows/EthanCarollo/rift-operation-workflow"

# The prompt based on user's preference
PROMPT = """
steel katana sword in a cartoon style.
"""

async def run_workflow():
    if not os.path.exists(INPUT_IMAGE):
        print(f"❌ Error: {INPUT_IMAGE} not found")
        return

    print("=" * 60)
    print(f"🚀 Running Fal.ai Workflow: {WORKFLOW_ID}")
    print("=" * 60)

    start_time = time.time()
    
    # Step 1: Load and encode image as base64 data URI
    print(f"\n📷 Loading {INPUT_IMAGE} as base64 data URI...")
    encode_start = time.time()
    with open(INPUT_IMAGE, 'rb') as f:
        image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_data_uri = f"data:image/png;base64,{image_base64}"
    encode_time = time.time() - encode_start
    print(f"   ✅ Encoded in {encode_time:.2f}s! ({len(image_bytes) / 1024:.1f} KB)")

    # Step 2: Execute Workflow
    print(f"\n🔄 Executing workflow...")
    workflow_start = time.time()
    
    stream = fal_client.stream_async(
        WORKFLOW_ID,
        arguments={
            "prompt": PROMPT,
            "image_url_field": image_data_uri
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
    print("\n💾 Saving results...")
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
                
                filename = f"output/workflow_{timestamp}_{i}.png"
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                print(f"   ✅ Saved to: {filename}")
            else:
                print(f"   ❌ Failed to download result {i+1}: {img_url}")
    
    save_time = time.time() - save_start
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("⏱️  TIMING SUMMARY")
    print("=" * 60)
    print(f"   Encode Image............................ {encode_time:>8.2f}s")
    print(f"   Workflow Execution...................... {workflow_time:>8.2f}s")
    print(f"   Save.................................... {save_time:>8.2f}s")
    print("-" * 60)
    print(f"   Total................................... {total_time:>8.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_workflow())
