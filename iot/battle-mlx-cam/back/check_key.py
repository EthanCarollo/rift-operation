
import os
import sys
import requests
from dotenv import load_dotenv

def check_key():
    # Load .env explicitly
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    
    key = os.getenv("FAL_KEY")
    
    if not key:
        print("❌ FAL_KEY not found in .env")
        return False
        
    print(f"🔑 checking key ending in ...{key[-4:]}")
    
    headers = {
        "Authorization": f"Key {key}",
        "Content-Type": "application/json"
    }
    
    url = "https://queue.fal.run/fal-ai/flux-kontext/dev"
    
    try:
        # We send an empty body.
        # - Valid key: 200 (In Queue) or 400/422 (Bad Request)
        # - Invalid key: 401 (Unauthorized)
        r = requests.post(url, headers=headers, json={}, timeout=10)
        
        if r.status_code == 401:
            print("❌ FAL_KEY is INVALID (401 Unauthorized)")
            return False
        
        if r.status_code == 403:
             print("❌ FAL_KEY is FORBIDDEN (403). Check quotas?")
             return False
             
        # Any other code (200, 400, 422, 500) means Auth passed
        print("✅ FAL_KEY is valid")
        print("ℹ️  (Credit balance cannot be checked via API, please check dashboard)")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not verify key: {e}")
        return True # Don't block start on connection error

if __name__ == "__main__":
    success = check_key()
    sys.exit(0 if success else 1)
