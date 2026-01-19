
import subprocess
import time
import os
import signal
import sys
import webbrowser
import argparse
from datetime import datetime
import json

# Global debug mode flag
DEBUG_MODE = False

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

    # Interactive screen selection
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

import sys
import tty
import termios

def get_key():
    """Get a single keypress from stdin."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\033': # Escape sequence
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def draw_menu(options, selected_index, last_line_count=0):
    """Draw the selection menu with a detail panel."""
    
    # Move cursor up to overwrite previous draw
    if last_line_count > 0:
        sys.stdout.write(f"\033[{last_line_count}A")
        
    lines = []
    
    # 1. Draw Menu Options
    lines.append(f"{Colors.HEADER}🌍 Select Environment (Arrow Keys to Move, Enter to Select):{Colors.ENDC}")
    lines.append("") # Spacer
    
    for idx, (label, _) in enumerate(options):
        prefix = "👉" if idx == selected_index else "  "
        if idx == selected_index:
            line = f"   {Colors.GREEN}{Colors.BOLD}{prefix} {label}{Colors.ENDC}"
        else:
            line = f"   {prefix} {label}"
        lines.append(line)
        
    lines.append("") # Spacer
    
    # 2. Draw Detail Panel for Slected Option
    _, vars_dict = options[selected_index]
    
    # Determine max dimensions
    if vars_dict:
        max_key_len = max([len(k) for k in vars_dict.keys()]) + 1 # +1 for colon
        max_val_len = max([len(str(v)) for v in vars_dict.values()])
    else:
        max_key_len = 0
        max_val_len = 0
            
    # Calculate box width: 2 chars (borders) + 2 chars (inner padding) + content + extra buffer
    content_width = max_key_len + 1 + max_val_len # +1 for space between key/val
    box_width = max(60, content_width + 4)
    
    # Box styles
    H_LINE = "─"
    V_LINE = "│"
    TL_CORNER = "╭"
    TR_CORNER = "╮"
    BL_CORNER = "╰"
    BR_CORNER = "╯"
    
    # Top Border
    lines.append(f"  {Colors.CYAN}{TL_CORNER}{H_LINE * (box_width - 2)}{TR_CORNER}{Colors.ENDC}")
    
    for key, val in vars_dict.items():
        # Prepare content parts
        key_str = f"{key}:".ljust(max_key_len + 1) # Left align key
        
        # Calculate padding needed to reach right border
        # Formula: box_width - 2 (borders) - 1 (left space) - len(key) - 1 (space) - len(val) - 1 (right space)
        # Actually simpler: we construct the raw string inside the box and pad it
        
        raw_content_len = len(key_str) + 1 + len(str(val)) # key + space + val
        padding = box_width - 2 - 1 - raw_content_len # -2 borders, -1 left indent
        
        if padding < 0: padding = 0 # Safety
        
        # Construct line: | Key: Val     |
        pad_str = " " * padding
        
        line = (f"  {Colors.CYAN}{V_LINE}{Colors.ENDC} "
                f"{Colors.BLUE}{key_str}{Colors.ENDC} "
                f"{Colors.BOLD}{val}{Colors.ENDC}"
                f"{pad_str}{Colors.CYAN}{V_LINE}{Colors.ENDC}")
        lines.append(line)
        
    # Bottom Border
    lines.append(f"  {Colors.CYAN}{BL_CORNER}{H_LINE * (box_width - 2)}{BR_CORNER}{Colors.ENDC}")
    
    # Print all lines
    for line in lines:
        sys.stdout.write(f"\033[K{line}\n")
        
    return len(lines)

def select_environment():
    """Prompts user to select Development or Production environment using arrow keys."""
    # Hide cursor
    sys.stdout.write("\033[?25l")
    
    options = [
        ("Development", {
            "WS_URL": "ws://server.riftoperation.ethan-folio.fr/ws",
            "NUXT_PUBLIC_BACKEND_URL": "http://localhost:5010",
            "NUXT_PUBLIC_WS_URL": "ws://server.riftoperation.ethan-folio.fr/ws"
        }),
        ("Production", {
            "WS_URL": "ws://192.168.10.7:8000/ws",
            "NUXT_PUBLIC_BACKEND_URL": "http://192.168.10.7:5010",
            "NUXT_PUBLIC_WS_URL": "ws://192.168.10.7:8000/ws"
        })
    ]
    
    selected_index = 0
    last_line_count = 0
    
    try:
        while True:
            last_line_count = draw_menu(options, selected_index, last_line_count)
            
            key = get_key()
            
            if key == '\033[A': # Up
                selected_index = max(0, selected_index - 1)
            elif key == '\033[B': # Down
                selected_index = min(len(options) - 1, selected_index + 1)
            elif key == '\r' or key == '\n': # Enter
                break
    finally:
        # Show cursor again
        sys.stdout.write("\033[?25h")
        
    name, vars_dict = options[selected_index]
    log(f"\n✅ Selected: {name} Mode", Colors.GREEN)
    
    # Merge with current environment
    env_vars = os.environ.copy()
    env_vars.update(vars_dict)
    
    return env_vars


# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACK_DIR = os.path.join(BASE_DIR, "back")
FRONT_DIR = os.path.join(BASE_DIR, "front")
CONDA_ENV_NAME = "rift-operation"

# Required ports
BACKEND_PORT = 5010
FRONTEND_PORT = 3010

def kill_port_processes():
    """Kill any processes running on required ports."""
    ports = [BACKEND_PORT, FRONTEND_PORT]
    
    for port in ports:
        try:
            # Find process using the port via lsof
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        log(f"🔪 Killing process {pid} on port {port}...", Colors.WARNING)
                        subprocess.run(["kill", "-9", pid], capture_output=True)
                log(f"✅ Port {port} cleared", Colors.GREEN)
        except Exception as e:
            log(f"⚠️ Could not clear port {port}: {e}", Colors.WARNING)

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
    
    # 0. Kill any processes on required ports
    kill_port_processes()
    
    # 0b. Check dependencies first
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

def start_backend(env_vars):
    log("🚀 Starting Backend (headless) on port 5010...", Colors.BLUE)
    # Use -u for unbuffered output so logs appear immediately
    cmd = ["conda", "run", "-n", CONDA_ENV_NAME, "--no-capture-output", "python", "-u", "main_headless.py"]
    return subprocess.Popen(cmd, cwd=BACK_DIR, preexec_fn=os.setsid, env=env_vars)

def start_frontend(env_vars):
    log("🚀 Starting Frontend (production) on port 3010...", Colors.CYAN)
    # Use preview to serve the built app
    cmd = ["npx", "nuxi", "preview", "--port", "3010", "--host", "0.0.0.0"]
    return subprocess.Popen(cmd, cwd=FRONT_DIR, preexec_fn=os.setsid, env=env_vars)

def open_browser(dream_screen=None, nightmare_screen=None):
    log("🌐 Opening Chrome windows in kiosk mode...", Colors.HEADER)
    if DEBUG_MODE:
        log("🔧 DEBUG MODE: DevTools will open automatically", Colors.WARNING)
    
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
            f"--window-size={screen['w']},{screen['h']}",
            "--kiosk",
            "--no-first-run",
            "--no-default-browser-check",
            "--use-fake-ui-for-media-stream",  # Auto-accept camera permission
            f"--unsafely-treat-insecure-origin-as-secure={url.split('/')[0]}//{url.split('/')[2]}", # Allow cam on HTTP
        ]
        
        # Add devtools flag if DEBUG_MODE is enabled
        if DEBUG_MODE:
            cmd.append("--auto-open-devtools-for-tabs")
        
        cmd.append(url)
        
        # Suppress Chrome stderr/stdout to avoid log spam
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Launch both windows (swapped: nightmare uses dream_screen, dream uses nightmare_screen)
    launch_kiosk(url_nightmare, dream_screen, "NIGHTMARE")
    time.sleep(0.5)
    launch_kiosk(url_dream, nightmare_screen, "DREAM")
        
    log("✅ Browser windows launched", Colors.GREEN)


def list_connected_cameras():
    """List available cameras using the backend function."""
    
    # Check for SSH session on macOS - CRASH if detected
    if os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'):
        log("🚫 SSH SESSION DETECTED - CANNOT RUN", Colors.FAIL)
        log("   macOS bloque l'accès caméra pour les sessions SSH/Remote.", Colors.FAIL)
        log("   Lancez ce script depuis le Terminal local de la machine.", Colors.FAIL)
        log("   (Ou via Screen Sharing/VNC)", Colors.WARNING)
        sys.exit(1)

    log("📷 Checking available cameras...", Colors.CYAN)
    try:
        # Run python script to list cameras
        cmd = [
            "conda", "run", "-n", CONDA_ENV_NAME,
            "python", "-c", "from src import list_cameras; print(list_cameras())"
        ]
        result = subprocess.run(cmd, cwd=BACK_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse output - it prints a list of tuples like [(0, 'Name'), ...]
            output = result.stdout.strip()
            # Basic cleanup of stdout if there are other prints
            lines = output.split('\n')
            camera_list_str = lines[-1] # The list should be the last thing printed
            
            try:
                # Safe eval to parse the string representation of list
                import ast
                cameras = ast.literal_eval(camera_list_str)
                
                if not cameras:
                    log("⚠️ No cameras detected!", Colors.WARNING)
                else:
                    log(f"✅ Found {len(cameras)} camera(s):", Colors.GREEN)
                    for idx, name in cameras:
                        print(f"   [{idx}] {name}")
            except:
                log(f"⚠️ Could not parse camera list: {camera_list_str}", Colors.WARNING)
        else:
            log(f"⚠️ Failed to list cameras: {result.stderr}", Colors.WARNING)
            
    except Exception as e:
        log(f"⚠️ Error checking cameras: {e}", Colors.WARNING)
    print("")



def check_fal_key():
    """Run the key check script."""
    log("🔑 Verifying FAL_KEY...", Colors.CYAN)
    try:
        cmd = ["conda", "run", "-n", CONDA_ENV_NAME, "python", "check_key.py"]
        subprocess.run(cmd, cwd=BACK_DIR, check=False)
    except Exception as e:
        log(f"⚠️ Key check failed: {e}", Colors.WARNING)
    print("")


    # Define log_configuration (stub to avoid errors if called elsewhere, or delete)
    # Actually, we should just delete the call in main since select_environment logs everything.

def check_ws_connection():
    """Run the WebSocket connection check."""
    # log("🔌 Verifying WebSocket Server...", Colors.CYAN) # Moved inside check_ws
    try:
        cmd = ["conda", "run", "-n", CONDA_ENV_NAME, "python", "check_ws.py"]
        subprocess.run(cmd, cwd=BACK_DIR, check=False)
    except Exception as e:
        log(f"⚠️ WS Check failed to run: {e}", Colors.WARNING)
    print("")

def main():
    back_proc = None
    front_proc = None

    try:
        # Setup environment first
        setup_environment()
        
        # Select Environment
        env_vars = select_environment()
        
        
        # 0. List cameras to help user debug
        list_connected_cameras()
        
        # 0b. Check API Key
        check_fal_key()
        
        # 0c. Check WebSocket Config
        # check_ws_connection() # Skip for now as direct script use might not match env vars
        
        back_proc = start_backend(env_vars)
        front_proc = start_frontend(env_vars)

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
    parser = argparse.ArgumentParser(description="Start Battle MLX Camera System")
    parser.add_argument("--debug", action="store_true", help="Open Chrome with DevTools console visible")
    args = parser.parse_args()
    
    DEBUG_MODE = args.debug
    
    main()
