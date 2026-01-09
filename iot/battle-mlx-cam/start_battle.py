
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

def start_backend():
    log("🚀 Starting Backend...", Colors.BLUE)
    # Ensure dependencies are installed
    # Use conda run to execute in the rift-operation environment
    cmd = ["conda", "run", "-n", "rift-operation", "python", "main.py"]
    # We use preexec_fn=os.setsid to easily kill the process tree later
    return subprocess.Popen(cmd, cwd=BACK_DIR, preexec_fn=os.setsid)

def start_frontend():
    log("🚀 Starting Frontend on port 3010...", Colors.CYAN)
    # Ensure dependencies are installed if needed, but here we assume yes
    cmd = ["npm", "run", "dev:battle"]
    return subprocess.Popen(cmd, cwd=FRONT_DIR, preexec_fn=os.setsid)

def open_browser(dream_screen=None, nightmare_screen=None):
    log("🌐 Opening Chrome windows...", Colors.HEADER)
    
    url_dream = "http://localhost:3010/?role=dream"
    url_nightmare = "http://localhost:3010/?role=nightmare"

    def launch_chrome_fullscreen(url, screen, role_name):
        """Launch Chrome and position using AppleScript for reliability."""
        if not screen:
            # Fallback: just open
            subprocess.Popen(["open", "-na", "Google Chrome", "--args", "--new-window", url])
            return
        
        # Get screen bounds (AppKit coordinates: bottom-left origin)
        # For AppleScript, we need top-left. macOS menubar is ~25px.
        # AppleScript bounds are {left, top, right, bottom}
        
        # AppKit: y=0 is bottom of main screen
        # To convert to AppleScript/top-left coords:
        # target_top = main_screen_height - (appkit_y + screen_height)
        
        main_h = NSScreen.screens()[0].frame().size.height
        
        # Screen bounds in AppKit
        sx = screen['x']
        sy = screen['y']
        sw = screen['w']
        sh = screen['h']
        
        # Convert to top-left coordinate system
        # The top of this screen in top-left coords:
        target_top = int(main_h - sy - sh)
        target_left = int(sx)
        target_right = int(sx + sw)
        target_bottom = int(main_h - sy)
        
        log(f"   {role_name}: Bounds = {{{target_left}, {target_top}, {target_right}, {target_bottom}}}", Colors.CYAN)
        
        # AppleScript to open URL in new window and set bounds
        applescript = f'''
        tell application "Google Chrome"
            activate
            set newWindow to make new window
            set URL of active tab of newWindow to "{url}"
            set bounds of newWindow to {{{target_left}, {target_top}, {target_right}, {target_bottom}}}
        end tell
        '''
        
        try:
            subprocess.run(["osascript", "-e", applescript], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            log(f"⚠️ AppleScript failed: {e.stderr.decode()}", Colors.WARNING)
            # Fallback
            subprocess.Popen(["open", "-na", "Google Chrome", "--args", "--new-window", url])

    # Launch Dream first
    launch_chrome_fullscreen(url_dream, dream_screen, "DREAM")
    time.sleep(0.5)
    
    # Launch Nightmare
    launch_chrome_fullscreen(url_nightmare, nightmare_screen, "NIGHTMARE")
        
    log("✅ Browser windows launched", Colors.GREEN)


def main():
    back_proc = None
    front_proc = None

    try:
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
        
        # Close Chrome windows opened by the script
        log("🌐 Closing Chrome battle windows...", Colors.CYAN)
        close_chrome_script = '''
        tell application "Google Chrome"
            set windowsToClose to {}
            repeat with w in windows
                set tabURL to URL of active tab of w
                if tabURL contains "localhost:3010" then
                    set end of windowsToClose to w
                end if
            end repeat
            repeat with w in windowsToClose
                close w
            end repeat
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", close_chrome_script], capture_output=True, timeout=5)
        except:
            pass
            
        log("💀 Backend and Frontend stopped.", Colors.FAIL)

if __name__ == "__main__":
    main()
