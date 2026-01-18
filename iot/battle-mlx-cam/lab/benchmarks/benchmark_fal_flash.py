#!/usr/bin/env python3
"""
Benchmark script for Flux 2 Flash Edit via FAL API.
"""
import os
import time
import sys
from dotenv import load_dotenv

# Add parent directory to path for src imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transform import transform_image

def main():
    # Load environment variables from parent dir
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(base_dir, "original.png")
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_flash_output.png")
    
    # Model configuration
    model_slug = "fal-ai/flux-2/flash/edit"
    prompt = "Transform this drawing into a realistic image of a golden antique key, detailed metalwork, soft shadows"

    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Reading {image_path}...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print(f"Starting benchmark for {model_slug}...")
    print(f"Prompt: {prompt}")
    
    try:
        start_time = time.time()
        output_bytes, elapsed = transform_image(image_bytes, prompt, model=model_slug)
        total_script_time = time.time() - start_time
        
        print("\n" + "="*50)
        print(f"BENCHMARK RESULTS: {model_slug}")
        print("="*50)
        print(f"API Reported Time: {elapsed:.2f}s")
        print(f"Total Script Time:  {total_script_time:.2f}s")
        print("="*50)

        if output_bytes:
            with open(output_path, "wb") as f:
                f.write(output_bytes)
            print(f"Result saved to {output_path}")
            
    except Exception as e:
        print(f"Error during transformation: {e}")

if __name__ == "__main__":
    main()
