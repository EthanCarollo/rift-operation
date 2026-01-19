#!/usr/bin/env python3
"""
Benchmark script for Replicate Flux 2 Klein 4b via API with Colors.
"""
import os
import time
import base64
import requests
import json
from dotenv import load_dotenv

# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    # Load environment variables
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    load_dotenv(env_path)
    
    api_token = os.getenv("REPLICATE_URL_API")
    if not api_token:
        print(f"{Colors.FAIL}Error: REPLICATE_URL_API not found in .env{Colors.ENDC}")
        return

    image_path = os.path.join(base_dir, "original.png")
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_replicate_output.jpg")
    
    model_slug = "black-forest-labs/flux-2-klein-4b"
    api_url = f"https://api.replicate.com/v1/models/{model_slug}/predictions"

    if not os.path.exists(image_path):
        print(f"{Colors.FAIL}Error: {image_path} not found.{Colors.ENDC}")
        return

    # STEP 1: Image to bytes
    print(f"{Colors.OKCYAN}Step 1: Converting image to bytes...{Colors.ENDC}")
    prep_start = time.time()
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        data_uri = f"data:image/png;base64,{b64_image}"
    
    prep_time = time.time() - prep_start
    print(f"{Colors.OKGREEN}✓ Preprocessing complete in {prep_time:.4f}s{Colors.ENDC}")

    prompt = "Transform this drawing into a realistic image of a golden antique key, detailed metalwork, soft shadows"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    
    payload = {
        "input": {
            "images": [data_uri],
            "prompt": prompt,
            "go_fast": False,
            "aspect_ratio": "1:1",
            "output_format": "jpg",
            "output_quality": 95,
            "output_megapixels": "1"
        }
    }

    print(f"\n{Colors.BOLD}Starting benchmark for Replicate {model_slug}...{Colors.ENDC}")
    print(f"{Colors.WARNING}Prompt: {prompt}{Colors.ENDC}")
    
    # STEP 2: Request
    print(f"{Colors.OKCYAN}Step 2: Sending request and waiting for inference...{Colors.ENDC}")
    req_start = time.time()
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code not in [200, 201]:
            print(f"{Colors.FAIL}❌ API Error: HTTP {response.status_code}{Colors.ENDC}")
            print(response.text)
            return

        result = response.json()
        
        # Poll if not finished
        while result.get("status") not in ["succeeded", "failed", "canceled"]:
            print(f"   Status: {Colors.OKBLUE}{result.get('status')}{Colors.ENDC}...")
            time.sleep(1)
            get_url = result["urls"]["get"]
            result = requests.get(get_url, headers=headers, timeout=30).json()

        req_time = time.time() - req_start
        
        if result.get("status") == "succeeded":
            output_url = result.get("output")
            if isinstance(output_url, list):
                output_url = output_url[0]
            
            print("\n" + f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.OKGREEN}BENCHMARK RESULTS: {model_slug}{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Image to Bytes Time: {Colors.ENDC} {prep_time:.4f}s")
            print(f"{Colors.OKGREEN}Total Request Time:  {Colors.ENDC} {req_time:.2f}s")
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")

            if output_url:
                img_resp = requests.get(output_url)
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                print(f"{Colors.OKCYAN}Result saved to:{Colors.ENDC} {output_path}")
        else:
            print(f"{Colors.FAIL}Prediction failed with status: {result.get('status')}{Colors.ENDC}")
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"{Colors.FAIL}Error during transformation: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
