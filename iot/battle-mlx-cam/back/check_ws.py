
import sys
import os
import time

# Add src to path to import config if needed, or just parse the file
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8000/ws")
except ImportError:
    print("⚠️ dotenv missing, checking default...")
    WS_URL = "ws://127.0.0.1:8000/ws" 

def check_ws():
    print(f"🔌 Testing WebSocket connection to: {WS_URL} ...")
    
    try:
        import websocket
        # Simple blocking connection test
        ws = websocket.create_connection(WS_URL, timeout=3)
        print("✅ WebSocket connection successful!")
        ws.close()
        return True
    except websocket.WebSocketTimeoutException:
        print("⚠️ Connection timed out")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused (server not running?)")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = check_ws()
    sys.exit(0 if success else 1)
