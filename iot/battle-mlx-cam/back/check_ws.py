
import sys
import os
import websocket
import time

# Add src to path to import config if needed, or just parse the file
# Ideally we import the constant to be truthful to the code
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from src.websocket_client import WS_URL
except ImportError:
    # Fallback if import fails (e.g. structure issues)
    # We will try to grep it or just default (but import is better)
    print("⚠️ Could not import WS_URL, checking default local...")
    WS_URL = "ws://192.168.10.7:8000/ws" 

def check_ws():
    print(f"🔌 Testing WebSocket connection to: {WS_URL} ...")
    
    result = {"success": False}
    
    def on_open(ws):
        print("✅ WebSocket connection successful!")
        result["success"] = True
        ws.close()
    
    def on_error(ws, error):
        print(f"❌ WebSocket Error: {error}")
        
    def on_close(ws, close_status_code, close_msg):
        pass

    # Try to connect with a short timeout
    ws = websocket.WebSocketApp(WS_URL,
                                on_open=on_open,
                                on_error=on_error,
                                on_close=on_close)
    
    # Run loop for max 3 seconds
    start_time = time.time()
    try:
        # We need to run run_forever in a way that respects timeout? 
        # Actually run_forever is blocking. We can use a thread or just rely on sockopt timeout
        # But for a simple check, a timeout in run_forever is hard.
        # Let's use simple socket create_connection to test availability first?
        # No, let's use the library but with a trick or just simple timeout.
        
        # Simpler approach:
        ws.run_forever(ping_timeout=2)
        
        if result["success"]:
            return True
        else:
            print("⚠️ Connection failed (timeout or refused)")
            return False
            
    except Exception as e:
        print(f"❌ Connection check crashed: {e}")
        return False

if __name__ == "__main__":
    success = check_ws()
    sys.exit(0 if success else 1)
