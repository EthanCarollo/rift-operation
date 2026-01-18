#!/usr/bin/env python3
"""
Master Benchmark Script - Compares all Flux models across Fal.ai and Replicate.
"""
import os
import time
import base64
import requests
import json
import sys
from dotenv import load_dotenv

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    GOLD = '\033[33m'
    SILVER = '\033[37m'
    BRONZE = '\033[31m'

# Add parent directory to path for src imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transform import transform_image

def run_fal_benchmark(model_slug, name, image_bytes, prompt, api_key):
    print(f"{Colors.OKCYAN}🚀 Testing Fal.ai: {Colors.BOLD}{name}{Colors.ENDC}...")
    try:
        start = time.time()
        # src.transform.transform_image already handles resizing and base64
        # We'll just measure the call
        _, elapsed_api = transform_image(image_bytes, prompt, model=model_slug, api_key=api_key)
        total_time = time.time() - start
        print(f"{Colors.OKGREEN}   ✓ Complete: {total_time:.2f}s{Colors.ENDC}")
        return total_time
    except Exception as e:
        print(f"{Colors.FAIL}   ❌ Error: {e}{Colors.ENDC}")
        return None

def run_replicate_benchmark(model_slug, name, image_bytes, prompt, api_token, input_transform=None):
    print(f"{Colors.OKCYAN}🚀 Testing Replicate: {Colors.BOLD}{name}{Colors.ENDC}...")
    api_url = f"https://api.replicate.com/v1/models/{model_slug}/predictions"
    
    # Preprocessing
    prep_start = time.time()
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    data_uri = f"data:image/png;base64,{b64_image}"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    
    payload = {"input": input_transform(data_uri, prompt) if input_transform else {"prompt": prompt}}
    
    try:
        start = time.time()
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        if response.status_code not in [200, 201]:
            print(f"{Colors.FAIL}   ❌ API Error: HTTP {response.status_code}{Colors.ENDC}")
            return None
        
        result = response.json()
        while result.get("status") not in ["succeeded", "failed", "canceled"]:
            time.sleep(1)
            result = requests.get(result["urls"]["get"], headers=headers, timeout=30).json()
        
        total_time = time.time() - start
        if result.get("status") == "succeeded":
            print(f"{Colors.OKGREEN}   ✓ Complete: {total_time:.2f}s{Colors.ENDC}")
            return total_time
        else:
            print(f"{Colors.FAIL}   ❌ Prediction failed{Colors.ENDC}")
            return None
    except Exception as e:
        print(f"{Colors.FAIL}   ❌ Error: {e}{Colors.ENDC}")
        return None

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, ".env"))
    
    fal_key = os.getenv("FAL_KEY")
    replicate_token = os.getenv("REPLICATE_URL_API")
    
    image_path = os.path.join(base_dir, "original.png")
    prompt = "Transform this drawing into a realistic image of a golden antique key, detailed metalwork, soft shadows"
    
    if not os.path.exists(image_path):
        print(f"{Colors.FAIL}Error: {image_path} not found.{Colors.ENDC}")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    results = []

    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{'FLUX MODEL BENCHMARK MASTER':^60}")
    print(f"{'='*60}{Colors.ENDC}\n")

    # 1. Fal.ai Klein
    t = run_fal_benchmark("fal-ai/flux-2/klein/4b/edit", "Fal.ai - Klein 4b", image_bytes, prompt, fal_key)
    if t: results.append({"name": "Fal.ai - Klein 4b", "time": t})

    # 2. Fal.ai Flash
    t = run_fal_benchmark("fal-ai/flux-2/flash/edit", "Fal.ai - Flash", image_bytes, prompt, fal_key)
    if t: results.append({"name": "Fal.ai - Flash", "time": t})

    # 3. Replicate Klein
    def rep_klein_input(uri, p): return {"images": [uri], "prompt": p, "go_fast": False, "output_format": "jpg"}
    t = run_replicate_benchmark("black-forest-labs/flux-2-klein-4b", "Replicate - Klein 4b", image_bytes, prompt, replicate_token, rep_klein_input)
    if t: results.append({"name": "Replicate - Klein 4b", "time": t})

    # 4. Replicate Pruna AI
    def pruna_input(uri, p): return {"img_cond_path": uri, "prompt": p, "speed_mode": "Extra Juiced 🔥 (more speed)", "output_format": "jpg"}
    t = run_replicate_benchmark("prunaai/flux-kontext-fast", "Replicate - Pruna AI Fast", image_bytes, prompt, replicate_token, pruna_input)
    if t: results.append({"name": "Replicate - Pruna AI Fast", "time": t})

    # RANKING
    results.sort(key=lambda x: x["time"])
    
    print("\n\n" + f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'🏆 FINAL RANKING 🏆':^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    medals = ["🥇", "🥈", "🥉", "  "]
    for i, res in enumerate(results):
        medal = medals[i] if i < len(medals) else "  "
        color = Colors.GOLD if i == 0 else Colors.SILVER if i == 1 else Colors.BRONZE if i == 2 else ""
        
        print(f"{medal} {color}{res['name']:<30}{Colors.ENDC} | {Colors.BOLD}{res['time']:>6.2f}s{Colors.ENDC}")

    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")

if __name__ == "__main__":
    main()
