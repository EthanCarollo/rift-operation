import subprocess
import time
import os
import sys
import shutil

def run_command(command, cwd=None, background=False):
    print(f"Running: {command}")
    try:
        if background:
            return subprocess.Popen(command, shell=True, cwd=cwd)
        else:
            subprocess.run(command, shell=True, check=True, cwd=cwd)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def find_chromium():
    if shutil.which("chromium"):
        return "chromium"
    
    # Common Mac paths
    possible_paths = [
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/opt/homebrew/bin/chromium", 
        "/usr/local/bin/chromium"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return f'"{path}"'
            
    print("Warning: Chromium not found in standard locations. Trying 'chromium' anyway.")
    return "chromium"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("--- 1. Building Application ---")
    run_command("npm run build", cwd=script_dir)
    
    print("\n--- 2. Starting Server ---")
    # 'npm run preview' runs the built application
    server_process = run_command("npm run preview", cwd=script_dir, background=True)
    
    print("Waiting 5 seconds for server to start...")
    time.sleep(5)
    
    print("\n--- 3. Launching Chromium in Kiosk Mode ---")
    chromium_bin = find_chromium()
    url = "http://localhost:3000"
    
    # --kiosk for full screen
    # --app to look like an app
    # --noerrdialogs to avoid error popups
    # --disable-infobars to remove "Chrome is being controlled..."
    browser_cmd = f'{chromium_bin} --kiosk --app={url} --noerrdialogs --disable-infobars'
    
    browser_process = run_command(browser_cmd, background=True)
    
    print("\nApp launched. Press Ctrl+C to stop everything.")
    
    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if server_process.poll() is not None:
                print("Server process died unexpectedly.")
                break
            if browser_process.poll() is not None:
                print("Browser process closed.")
                break
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if server_process:
            server_process.terminate()
        if browser_process:
            browser_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
