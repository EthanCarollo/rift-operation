import subprocess
import time
import os
import sys
import shutil
import signal
import glob

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

def configure_display_env():
    """Sets DISPLAY and XAUTHORITY search."""
    if "DISPLAY" not in os.environ:
        log("DISPLAY environment variable not detected. Defaulting to ':0'.", "WARNING")
        os.environ["DISPLAY"] = ":0"
    
    if "XAUTHORITY" not in os.environ:
        # Search strategy for Xauthority
        possible_auths = []
        
        # 1. Standard home location
        possible_auths.append(os.path.join(os.path.expanduser("~"), ".Xauthority"))
        
        # 2. Runtime directories (common in modern GDM/Ubuntu)
        try:
            uid = os.getuid()
            possible_auths.append(f"/run/user/{uid}/gdm/Xauthority")
            possible_auths.append(f"/run/user/{uid}/Xauthority")
            # Also check for any Xauthority file in /run/user/{uid}/
            possible_auths.extend(glob.glob(f"/run/user/{uid}/Xauthority*"))
        except Exception:
            pass

        found_auth = None
        for path in possible_auths:
            if os.path.exists(path):
                found_auth = path
                break
        
        if found_auth:
            log(f"Found Xauthority at {found_auth}. Exporting env var.", "SUCCESS")
            os.environ["XAUTHORITY"] = found_auth
        else:
            log("Could not find a valid Xauthority file. GUI operations may fail.", "WARNING")

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
    
    # We pass the current environment (including newly set DISPLAY/XAUTHORITY) to subprocess
    # We allow failure because xset might fail if we are headless or if X isn't ready, but we don't want to abort
    for cmd in commands:
        try:
            run_command(cmd, env=os.environ, background=False, allow_failure=True)
        except Exception:
            pass
    log("Screen settings updated.", "SUCCESS")

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
    
    # Fix for Display/Auth
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
    # --app to look like an app
    # --noerrdialogs to avoid error popups
    # --disable-infobars to remove "Chrome is being controlled..."
    # --start-fullscreen alternate flag
    browser_cmd = f'{chromium_bin} --kiosk --app={url} --noerrdialogs --disable-infobars'
    
    log(f"Launching Kiosk Mode at {url}...", "INFO")
    # Pass os.environ to ensure DISPLAY/XAUTHORITY are passed to Chromium
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
