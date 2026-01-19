import subprocess
import time
import os
import sys
import shutil
import signal

def run_command(command, cwd=None, background=False, env=None):
    print(f"Running: {command}")
    
    # Merge current environment with provided env
    command_env = os.environ.copy()
    if env:
        command_env.update(env)

    try:
        if background:
            # start_new_session=True sets the child process as a new process group leader
            # This allows us to kill the whole group later
            return subprocess.Popen(command, shell=True, cwd=cwd, env=command_env, start_new_session=True)
        else:
            subprocess.run(command, shell=True, check=True, cwd=cwd, env=command_env)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        raise e

def clean_and_recover(script_dir):
    print("\n!!! Error detected during install/build !!!")
    print("Performing clean recovery...")
    
    node_modules = os.path.join(script_dir, "node_modules")
    package_lock = os.path.join(script_dir, "package-lock.json")
    
    if os.path.exists(node_modules):
        print(f"Removing {node_modules}...")
        shutil.rmtree(node_modules)
        
    if os.path.exists(package_lock):
        print(f"Removing {package_lock}...")
        os.remove(package_lock)
        
    print("Cleaning npm cache...")
    try:
        run_command("npm cache clean --force", cwd=script_dir)
    except Exception as e:
        print(f"Warning: Failed to clean npm cache: {e}")

def install_and_build(script_dir):
    try:
        print("--- 1. Installing Dependencies ---")
        run_command("npm install", cwd=script_dir)
        
        # User requested explicitly REMOVING npm audit fix
        # print("--- 1b. Running Audit Fix ---")
        # run_command("npm audit fix", cwd=script_dir) ...

        print("--- 2. Building Application ---")
        run_command("npm run build", cwd=script_dir)
        
    except subprocess.CalledProcessError:
        clean_and_recover(script_dir)
        
        print("\n--- Retrying Install and Build ---")
        try:
            run_command("npm install", cwd=script_dir)
            run_command("npm run build", cwd=script_dir)
        except subprocess.CalledProcessError:
            print("\n!!! Critical Error: Failed to install/build even after recovery. !!!")
            sys.exit(1)

def ensure_chromium_installed():
    """Checks if chromium is installed. If not, attempts to install it (Ubuntu/Debian)."""
    if shutil.which("chromium") or shutil.which("chromium-browser"):
        return
    
    # Not found - try to install
    print("\n!!! Chromium not found. Attempting to install... !!!")
    try:
        # Using sudo - assume user can run sudo or will be prompted
        run_command("sudo apt-get update && sudo apt-get install chromium-browser -y")
    except Exception as e:
        print(f"Failed to install chromium: {e}")
        print("Please install Chromium manually: sudo apt install chromium-browser")

def wake_screen():
    """Attempts to wake the screen and disable sleep."""
    print("--- 0. Waking Screen / Disabling Sleep ---")
    commands = [
        "xset dpms force on", # Force screen on
        "xset s off",         # Disable screen saver timeout
        "xset -dpms",         # Disable energy star features
        "xset s noblank"      # Don't blank the video device
    ]
    for cmd in commands:
        try:
            # We ignore errors here because xset might not be available or applicable (e.g. Wayland without XWayland, or Mac)
            subprocess.run(cmd, shell=True, check=False)
        except Exception:
            pass

def find_chromium():
    # First check standard binaries
    if shutil.which("chromium-browser"):
        return "chromium-browser"
    if shutil.which("chromium"):
        return "chromium"
    
    # Common Mac paths (fallback if user runs on Mac)
    possible_paths = [
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/opt/homebrew/bin/chromium", 
        "/usr/local/bin/chromium"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return f'"{path}"'
            
    print("Warning: Chromium not found in standard locations. Using 'chromium' as fallback.")
    return "chromium"

def kill_process_group(process):
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass # Already dead

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 0. Wake Screen
    wake_screen()
    
    # Check/Install Chromium (Ubuntu logic included)
    ensure_chromium_installed()
    
    # 1 & 2. Install and Build (with auto-recovery)
    install_and_build(script_dir)
    
    print("\n--- 3. Starting Server on Port 3098 ---")
    # Set PORT and NITRO_PORT to 3098
    env_vars = {"PORT": "3098", "NITRO_PORT": "3098"}
    
    # 'npm run preview' runs the built application
    server_process = run_command("npm run preview", cwd=script_dir, background=True, env=env_vars)
    
    print("Waiting 5 seconds for server to start...")
    time.sleep(5)
    
    print("\n--- 4. Launching Chromium in Kiosk Mode ---")
    chromium_bin = find_chromium()
    url = "http://localhost:3098"
    
    # --kiosk for full screen
    # --app to look like an app
    # --noerrdialogs to avoid error popups
    # --disable-infobars to remove "Chrome is being controlled..."
    # --start-fullscreen alternate flag
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
        print("Cleaning up processes...")
        kill_process_group(server_process)
        kill_process_group(browser_process)
        sys.exit(0)

if __name__ == "__main__":
    main()
