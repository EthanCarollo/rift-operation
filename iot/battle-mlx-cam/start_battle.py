
import subprocess
import time
import os
import signal
import sys
import webbrowser
from datetime import datetime
import json

# Check for AppKit availability (will use subprocess to run via conda if needed, or import directly)
try:
    from AppKit import NSScreen
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, color=Colors.ENDC):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

def get_connected_screens():
    """
    Returns a list of screens with their index, frame (x, y, w, h).
    Uses AppKit.
    """
    if HAS_APPKIT:
        screens = []
        for i, screen in enumerate(NSScreen.screens()):
            frame = screen.frame()
            # NSScreen origin is bottom-left. Chrome/System often expect top-left logic, but --window-position usually takes screen coordinates.
            # However, for multi-monitor, macOS coordinates: (0,0) is bottom-left of main screen.
            # We might need to handle coordinate flipping if Chrome behaves oddly, but let's trust standard frame origin first.
            # Actually, AppKit (0,0) is bottom-left. Windows usually expect top-left.
            # Let's just grab the origin x, and the flipped y if needed.
            # To simplify, we'll just store struct.
            
            # frame is NSRect (origin, size)
            x = frame.origin.x
            y = frame.origin.y 
            w = frame.size.width
            h = frame.size.height
            
            # Main screen height (for coordinate conversion if needed)
            main_h = NSScreen.screens()[0].frame().size.height
            
            # Convert to top-left coordinates for Chrome
            # y_top_left = main_screen_height - (y_bottom_left + height)
            # Wait, screen coordinates in Quartz/AppKit:
            # (0,0) is bottom-left of main screen.
            # Screen 2 might be at (-1920, 0) etc.
            # Chrome expects screen coordinates.
            # Visual layout: Main screen (0,0) top-left usually in window managers, but AppKit is bottom-left.
            # Let's try to just use x,y and see.
            
            screens.append({
                "index": i,
                "x": int(x),
                "y": int(y), # We might need to fix this for Chrome
                "w": int(w),
                "h": int(h),
                "name": f"Display {i}"
            })
        return screens
        
    # Fallback: try running this function in the conda env if we aren't already
    # This is a bit recursive, but simpler is to just assume user has it or we fail gracefully.
    return []

def select_screens():
    screens = get_connected_screens()
    if not screens:
        log("⚠️ No screens detected (AppKit missing?). Using defaults.", Colors.WARNING)
        return None, None

    log("\n🖥️  Connected Displays:", Colors.HEADER)
    for s in screens:
        print(f"   [{s['index']}] {s['w']}x{s['h']} at ({s['x']},{s['y']})")
    
    print("")
    
    def ask(role):
        while True:
            try:
                val = input(f"{Colors.BLUE}Select Display for {role} (0-{len(screens)-1}): {Colors.ENDC}")
                idx = int(val)
                if 0 <= idx < len(screens):
                    return screens[idx]
            except ValueError:
                pass
            print("Invalid selection.")

    dream_screen = ask("DREAM")
    nightmare_screen = ask("NIGHTMARE")
    
    return dream_screen, nightmare_screen

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACK_DIR = os.path.join(BASE_DIR, "back")
FRONT_DIR = os.path.join(BASE_DIR, "front")
CONDA_ENV_NAME = "rift-operation"

def check_dependencies():
    """Check if brew and conda are installed, provide installation instructions if not."""
    
    # Check for brew
    brew_check = subprocess.run(["which", "brew"], capture_output=True, text=True)
    if brew_check.returncode != 0:
        log("❌ Homebrew is not installed!", Colors.FAIL)
        log("   Run this command to install Homebrew:", Colors.WARNING)
        log('   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', Colors.CYAN)
        return False
    
    # Check for conda
    conda_check = subprocess.run(["which", "conda"], capture_output=True, text=True)
    if conda_check.returncode != 0:
        log("❌ Conda is not installed!", Colors.FAIL)
        log("   Run this command to install Anaconda via Homebrew:", Colors.WARNING)
        log("   brew install --cask anaconda", Colors.CYAN)
        log("   Then add conda to your PATH and restart your terminal.", Colors.WARNING)
        return False
    
    return True

def setup_environment():
    """Setup conda environment and install dependencies."""
    
    # 0. Check dependencies first
    if not check_dependencies():
        log("⚠️ Please install the missing dependencies and try again.", Colors.FAIL)
        sys.exit(1)
    
    # 1. Check if conda env exists, create if not
    log("🔍 Checking conda environment...", Colors.CYAN)
    result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
    
    if CONDA_ENV_NAME not in result.stdout:
        log(f"📦 Creating conda environment '{CONDA_ENV_NAME}'...", Colors.WARNING)
        subprocess.run(["conda", "create", "-n", CONDA_ENV_NAME, "python=3.10", "-y"], check=True)
    else:
        log(f"✅ Conda environment '{CONDA_ENV_NAME}' exists", Colors.GREEN)
    
    # 2. Install Python dependencies in conda env
    log("📦 Installing Python dependencies (back)...", Colors.CYAN)
    subprocess.run([
        "conda", "run", "-n", CONDA_ENV_NAME, 
        "pip", "install", "-r", "requirements.txt", "-q"
    ], cwd=BACK_DIR, check=True)
    log("✅ Python dependencies installed", Colors.GREEN)
    
    # 3. Install npm dependencies for frontend
    log("📦 Installing npm dependencies (front)...", Colors.CYAN)
    subprocess.run(["npm", "install"], cwd=FRONT_DIR, check=True, capture_output=True)
    log("✅ npm dependencies installed", Colors.GREEN)
    
    # 4. Build frontend for production
    log("🔨 Building frontend...", Colors.CYAN)
    subprocess.run(["npm", "run", "build"], cwd=FRONT_DIR, check=True, capture_output=True)
    log("✅ Frontend built", Colors.GREEN)

def start_backend():
    log("🚀 Starting Backend on port 5000...", Colors.BLUE)
    cmd = ["conda", "run", "-n", CONDA_ENV_NAME, "python", "main.py"]
    return subprocess.Popen(cmd, cwd=BACK_DIR, preexec_fn=os.setsid)

def start_frontend():
    log("🚀 Starting Frontend (production) on port 3010...", Colors.CYAN)
    # Use preview to serve the built app
    cmd = ["npx", "nuxi", "preview", "--port", "3010", "--host", "0.0.0.0"]
    return subprocess.Popen(cmd, cwd=FRONT_DIR, preexec_fn=os.setsid)

def open_browser(dream_screen=None, nightmare_screen=None):
    log("🌐 Opening Chrome windows in kiosk mode...", Colors.HEADER)
    
    url_dream = "http://localhost:3010/?role=dream"
    url_nightmare = "http://localhost:3010/?role=nightmare"
    
    chrome_exe = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    def launch_kiosk(url, screen, role_name):
        """Launch Chrome in kiosk mode on specific screen."""
        if not screen:
            subprocess.Popen(["open", "-na", "Google Chrome", "--args", "--kiosk", url])
            return
        
        # Chrome kiosk mode with window position
        # Use unique user-data-dir to allow multiple instances
        user_data = f"/tmp/chrome_battle_{role_name.lower()}"
        
        # Calculate position for this screen
        main_h = NSScreen.screens()[0].frame().size.height
        target_x = int(screen['x'])
        target_y = int(main_h - screen['y'] - screen['h'])
        
        log(f"   {role_name}: Position ({target_x}, {target_y}), Size {screen['w']}x{screen['h']}", Colors.CYAN)
        
        cmd = [
            chrome_exe,
            f"--user-data-dir={user_data}",
            f"--window-position={target_x},{target_y}",
            f"--window-size={screen['w']},{screen['h']}",
            "--kiosk",
            "--no-first-run",
            "--no-default-browser-check",
            url
        ]
        
        # Suppress Chrome stderr/stdout to avoid log spam
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Launch both windows
    launch_kiosk(url_dream, dream_screen, "DREAM")
    time.sleep(0.5)
    launch_kiosk(url_nightmare, nightmare_screen, "NIGHTMARE")
        
    log("✅ Browser windows launched", Colors.GREEN)


def main():
    back_proc = None
    front_proc = None

    try:
        # Setup environment first
        setup_environment()
        
        back_proc = start_backend()
        front_proc = start_frontend()

        log("⏳ Waiting 10 seconds for services to come up...", Colors.WARNING)
        time.sleep(10)

        # Select screens
        dream_s, nightmare_s = select_screens()
        
        open_browser(dream_s, nightmare_s)

        log("✅ All Services running. Press Ctrl+C to stop.", Colors.GREEN)
        
        while True:
            time.sleep(1)
            
            # Check if processes are still alive
            if back_proc.poll() is not None:
                log("❌ Backend stopped unexpectedly.", Colors.FAIL)
                break
            if front_proc.poll() is not None:
                log("❌ Frontend stopped unexpectedly.", Colors.FAIL)
                break

    except KeyboardInterrupt:
        log("\n🛑 Stopping services...", Colors.WARNING)
    finally:
        if back_proc:
            try:
                os.killpg(os.getpgid(back_proc.pid), signal.SIGTERM)
            except:
                pass
        if front_proc:
            try:
                os.killpg(os.getpgid(front_proc.pid), signal.SIGTERM)
            except:
                pass
        
        # Close ALL Chrome windows by quitting Chrome
        log("🌐 Quitting Chrome...", Colors.CYAN)
        close_chrome_script = '''
        tell application "Google Chrome"
            quit
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", close_chrome_script], capture_output=True, timeout=5, text=True)
        except Exception as e:
            log(f"⚠️ Failed to quit Chrome: {e}", Colors.WARNING)
            
        log("💀 Backend and Frontend stopped.", Colors.FAIL)

if __name__ == "__main__":
    main()
