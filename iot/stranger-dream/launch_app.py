import subprocess
import time
import os
import sys
import shutil
import signal
import glob
import pwd
import re

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message, level="INFO"):
    prefix = ""
    color = Colors.ENDC
    if level == "SECTION":
        color = Colors.HEADER + Colors.BOLD
        prefix = "\n🚀 "
    elif level == "INFO":
        color = Colors.BLUE
        prefix = "ℹ️  "
    elif level == "SUCCESS":
        color = Colors.GREEN
        prefix = "✅ "
    elif level == "WARNING":
        color = Colors.WARNING
        prefix = "⚠️  "
    elif level == "ERROR":
        color = Colors.FAIL
        prefix = "❌ "
    elif level == "DEBUG":
        color = Colors.CYAN
        prefix = "🔍 "
    
    print(f"{color}{prefix}{message}{Colors.ENDC}")

def run_command(command, cwd=None, background=False, env=None, allow_failure=False):
    log(f"Executing: {command}", "INFO")
    
    # Merge current environment with provided env
    command_env = os.environ.copy()
    if env:
        command_env.update(env)

    try:
        if background:
            # start_new_session=True sets the child process as a new process group leader
            return subprocess.Popen(command, shell=True, cwd=cwd, env=command_env, start_new_session=True)
        else:
            subprocess.run(command, shell=True, check=True, cwd=cwd, env=command_env)
            return None
    except subprocess.CalledProcessError as e:
        if allow_failure:
            log(f"Command failed (non-critical): {e}", "WARNING")
            return None
        else:
            log(f"Command failed with error: {e}", "ERROR")
            raise e

def clean_and_recover(script_dir):
    log("Error detected during install/build process.", "ERROR")
    log("Initiating clean recovery protocol...", "WARNING")
    
    node_modules = os.path.join(script_dir, "node_modules")
    package_lock = os.path.join(script_dir, "package-lock.json")
    
    if os.path.exists(node_modules):
        log(f"Removing corrupted directory: {node_modules}", "INFO")
        shutil.rmtree(node_modules)
        
    if os.path.exists(package_lock):
        log(f"Removing lock file: {package_lock}", "INFO")
        os.remove(package_lock)
        
    log("Force cleaning npm cache...", "INFO")
    try:
        run_command("npm cache clean --force", cwd=script_dir)
    except Exception as e:
        log(f"Failed to clean npm cache: {e}", "WARNING")

def install_and_build(script_dir):
    try:
        log("Phase 1: Installing Dependencies", "SECTION")
        log("Installing npm packages...", "INFO")
        run_command("npm install", cwd=script_dir)
        log("Dependencies installed successfully.", "SUCCESS")
        
        log("Phase 2: Building Application", "SECTION")
        log("Building Nuxt application for production...", "INFO")
        run_command("npm run build", cwd=script_dir)
        log("Build completed successfully.", "SUCCESS")
        
    except subprocess.CalledProcessError:
        clean_and_recover(script_dir)
        
        log("Retrying Install and Build...", "SECTION")
        try:
            run_command("npm install", cwd=script_dir)
            run_command("npm run build", cwd=script_dir)
            log("Recovery successful! Application built.", "SUCCESS")
        except subprocess.CalledProcessError:
            log("Critical Error: Failed to recover. Please check logs and network connection.", "ERROR")
            sys.exit(1)

def ensure_chromium_installed():
    """Checks if chromium is installed. If not, attempts to install it (Ubuntu/Debian)."""
    if shutil.which("chromium") or shutil.which("chromium-browser"):
        return
    
    log("Chromium browser not found on system.", "WARNING")
    log("Attempting automatic installation (requires sudo)...", "INFO")
    try:
        run_command("sudo apt-get update && sudo apt-get install chromium-browser -y")
        log("Chromium installed successfully.", "SUCCESS")
    except Exception as e:
        log(f"Failed to install chromium: {e}", "ERROR")
        log("Please install Chromium manually: sudo apt install chromium-browser", "WARNING")

def get_real_user_info():
    """Gets the real user ID and home directory, even if running as sudo."""
    uid = os.getuid()
    username = os.environ.get("SUDO_USER")
    
    if username:
        try:
            pw = pwd.getpwnam(username)
            uid = pw.pw_uid
            home = pw.pw_dir
            return uid, home, username
        except KeyError:
            pass
            
    home = os.path.expanduser("~")
    try:
        username = os.getlogin()
    except Exception:
        username = "unknown"
    return uid, home, username

def detect_display(uid):
    """Attempts to find the active X display."""
    # 1. Existing Env
    if "DISPLAY" in os.environ:
        return os.environ["DISPLAY"]
    
    # 2. Check /tmp/.X11-unix
    try:
        sockets = glob.glob("/tmp/.X11-unix/X*")
        if sockets:
            # Sort to find the lowest number (usually X0)
            sockets.sort()
            display_num = sockets[0].split("X")[-1]
            return f":{display_num}"
    except Exception:
        pass
        
    # 3. Check 'w' command for user login (useful for SSH)
    try:
        output = subprocess.check_output("w -h", shell=True).decode()
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                # Check detection logic: USER TTY FROM ...
                 # if detected FROM is a display like :0 or :1
                 display_candidate = parts[2]
                 if display_candidate.startswith(":") and len(display_candidate) < 5:
                     return display_candidate
    except Exception:
        pass

    return ":0" # Final fallback

def find_xauth_from_processes():
    """Attempts to find the -auth argument in running X processes."""
    try:
        # Search for Xorg or Xwayland processes
        # Check running processes
        cmd = "ps aux | grep -v grep | grep -E 'Xorg|Xwayland|X11'"
        output = subprocess.check_output(cmd, shell=True).decode()
        
        for line in output.splitlines():
            # Look for -auth <path> pattern
            match = re.search(r'-auth\s+(\S+)', line)
            if match:
                path = match.group(1)
                # Verify it exists
                if os.path.exists(path):
                    return path
    except Exception:
        pass
    return None

def configure_display_env():
    """Sets DISPLAY, XAUTHORITY, and DBUS_SESSION_BUS_ADDRESS."""
    uid, user_home, username = get_real_user_info()
    log(f"Configuring environment for user: {username} (UID: {uid})", "SECTION")
    
    # 1. DISPLAY
    display = detect_display(uid)
    os.environ["DISPLAY"] = display
    log(f"Set DISPLAY={display}", "DEBUG")
    
    # 2. XAUTHORITY
    if "XAUTHORITY" not in os.environ:
        found_auth = None
        
        # Strategy A: Check standard paths
        possible_auths = []
        possible_auths.append(os.path.join(user_home, ".Xauthority"))
        possible_auths.append(f"/run/user/{uid}/gdm/Xauthority")
        possible_auths.append(f"/run/user/{uid}/Xauthority")
        possible_auths.extend(glob.glob(f"/run/user/{uid}/Xauthority*"))
        
        for path in possible_auths:
            if os.path.exists(path):
                found_auth = path
                break
        
        # Strategy B: Check running processes (Aggressive Fallback)
        if not found_auth:
            log("Standard Xauthority paths failed. Scanning process list...", "DEBUG")
            found_auth = find_xauth_from_processes()

        if found_auth:
            os.environ["XAUTHORITY"] = found_auth
            log(f"Set XAUTHORITY={found_auth}", "DEBUG")
        else:
            log(f"Could not find Xauthority. Candidates: {possible_auths}", "WARNING")

    # 3. DBUS SESSION for Chromium
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
        dbus_addr = f"unix:path=/run/user/{uid}/bus"
        if os.path.exists(f"/run/user/{uid}/bus"):
            os.environ["DBUS_SESSION_BUS_ADDRESS"] = dbus_addr
            log(f"Set DBUS_SESSION_BUS_ADDRESS={dbus_addr}", "DEBUG")
        else:
            log("Could not find /run/user/<uid>/bus. Chromium detection might fail.", "WARNING")

def wake_screen():
    """Attempts to wake the screen and disable sleep."""
    log("Phase 0: Environment Prep", "SECTION")
    log("Waking screen and disabling sleep modes...", "INFO")
    commands = [
        "xset dpms force on", # Force screen on
        "xset s off",         # Disable screen saver timeout
        "xset -dpms",         # Disable energy star features
        "xset s noblank"      # Don't blank the video device
    ]
    
    for cmd in commands:
        try:
            run_command(cmd, env=os.environ, background=False, allow_failure=True)
        except Exception:
            pass
            
    log("Screen settings update attempt complete.", "INFO")

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
            
    log("Chromium not found in standard locations. Using 'chromium' as fallback.", "WARNING")
    return "chromium"

def kill_process_group(process):
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass # Already dead

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"{Colors.HEADER}{Colors.BOLD}╔══════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}║      Stranger Dream Launch System        ║{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}╚══════════════════════════════════════════╝{Colors.ENDC}")
    
    # Fix for Display/Auth/DBus
    configure_display_env()
    
    # 0. Wake Screen (now uses the configured env)
    wake_screen()
    
    # Check/Install Chromium (Ubuntu logic included)
    ensure_chromium_installed()
    
    # 1 & 2. Install and Build (with auto-recovery)
    install_and_build(script_dir)
    
    log("Phase 3: Starting Web Server", "SECTION")
    # Set PORT and NITRO_PORT to 3098
    port = "3098"
    env_vars = {"PORT": port, "NITRO_PORT": port}
    
    log(f"Starting Nuxt preview server on port {port}...", "INFO")
    server_process = run_command("npm run preview", cwd=script_dir, background=True, env=env_vars)
    
    log("Waiting 5 seconds for server to initialize...", "INFO")
    time.sleep(5)
    
    log("Phase 4: Launching Interface", "SECTION")
    chromium_bin = find_chromium()
    url = f"http://localhost:{port}"
    
    # --kiosk for full screen
    # --noerrdialogs to avoid error popups
    # --disable-infobars to remove "Chrome is being controlled..."
    # --incognito to avoid session restore bubbles
    # --check-for-update-interval to disable updates
    # --overscroll-history-navigation=0 to disable swipe navigation
    # --disable-pinch to disable pinch zooming
    # --no-first-run to skip first run wizards
    # --fast-start
    # --disable-features=Translate,TranslateUI, bubble
    # --password-store=basic to avoid keyring prompts
    browser_cmd = (
        f'{chromium_bin} --kiosk "{url}" '
        '--noerrdialogs '
        '--disable-infobars '
        '--incognito '
        '--check-for-update-interval=31536000 '
        '--overscroll-history-navigation=0 '
        '--disable-pinch '
        '--touch-events=enabled '
        '--no-first-run '
        '--fast '
        '--fast-start '
        '--disable-features=Translate,TranslateUI,InfiniteSessionRestore,Bubble,SidePanelPinning '
        '--password-store=basic '
    )
    
    log(f"Launching Kiosk Mode at {url}...", "INFO")
    # Pass os.environ to ensure DISPLAY/XAUTHORITY/DBUS are passed to Chromium
    browser_process = run_command(browser_cmd, background=True, env=os.environ, allow_failure=True)
    
    log("System Fully Operational.", "SUCCESS")
    log("Press Ctrl+C to shutdown system safely.", "WARNING")
    
    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if server_process.poll() is not None:
                log("Server process died unexpectedly!", "ERROR")
                break
            if browser_process.poll() is not None:
                log("Browser process closed.", "WARNING")
                break
    except KeyboardInterrupt:
        print("\n")
        log("Shutdown sequence initiated...", "WARNING")
    finally:
        log("Cleaning up processes...", "INFO")
        kill_process_group(server_process)
        kill_process_group(browser_process)
        log("Cleanup complete. Goodbye!", "SUCCESS")
        sys.exit(0)

if __name__ == "__main__":
    main()
