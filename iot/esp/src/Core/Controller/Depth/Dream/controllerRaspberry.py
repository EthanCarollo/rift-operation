import threading
import time
import math
import struct
from typing import List, Set, Callable, Optional

# Monkey Patch: Silence struct.error in collision detection
try:
    from spherov2.commands.sensor import Sensor

    original_notify_helper = Sensor.collision_detected_notify[1]

    def safe_collision_notify_helper(listener, packet):
        try:
            original_notify_helper(listener, packet)
        except struct.error:
            pass
        except Exception as e:
            print(f"[COLLISION ERROR] {e}")

    Sensor.collision_detected_notify = (
        Sensor.collision_detected_notify[0],
        safe_collision_notify_helper
    )
except ImportError:
    pass

from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color

# ================= CONFIG =================
# List of target Sphero names to connect to. 
# TARGET_SPHERO_NAMES = ["SB-08C9", "SB-1219"] 
TARGET_SPHERO_NAMES = ["SB-08C9", "SB-1219", "SB-2020"] 
SHAKE_THRESHOLD = 2.0
SHAKE_COOLDOWN = 1.0  # seconds
SCAN_TIMEOUT = 5.0    # seconds
# ==========================================


class SpheroController:
    def __init__(self, target_names: List[str], on_shake_callback: Optional[Callable[[str, float], None]] = None):
        self.target_names = set(target_names)
        self.on_shake_callback = on_shake_callback
        self.active_devices: Set[str] = set()
        self.lock = threading.Lock()
        self.running = True

    def start(self):
        print(f"[INFO] Controller started. Targets: {', '.join(self.target_names)}")
        # Run the main discovery loop in a separate thread so it doesn't block if called from another script
        # checking if we are running as main or library
        if __name__ == "__main__":
            self._run_discovery_loop()
        else:
            t = threading.Thread(target=self._run_discovery_loop, daemon=True)
            t.start()

    def _run_discovery_loop(self):
        try:
            while self.running:
                # Calculate which devices are missing
                with self.lock:
                    missing = self.target_names - self.active_devices
                
                if not missing:
                    time.sleep(2)
                    continue

                print(f"[INFO] Scanning for missing devices: {', '.join(missing)}...")
                
                try:
                    available_toys = scanner.find_toys(timeout=SCAN_TIMEOUT)
                    
                    for toy in available_toys:
                        if toy.name in missing:
                            with self.lock:
                                if toy.name not in self.active_devices:
                                    self._launch_device_thread(toy)
                                    missing.discard(toy.name)
                
                except Exception as e:
                    print(f"[WARN] Scan failed: {e}")
                
                if missing:
                    time.sleep(2)

        except KeyboardInterrupt:
            print("\n[INFO] Stopping controller...")
            self.running = False
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[FATAL ERROR] {e}")

    def _launch_device_thread(self, toy):
        name = toy.name
        print(f"[INFO] Found target: {name}. Launching thread...")
        
        self.active_devices.add(name)
        
        t = threading.Thread(target=self._monitor_toy, args=(toy,), daemon=True)
        t.start()
        
        time.sleep(2.0)

    def _monitor_toy(self, toy):
        name = toy.name
        shake_cooldown = 0
        
        try:
            print(f"[{name}] Attempting to connect...")
            with SpheroEduAPI(toy) as droid:
                droid.set_main_led(Color(0, 255, 0))
                print(f"\n✅ [{name}] CONNECTED SUCCESSFULLY!")
                print(f"   Listening for shakes on [{name}]...\n")

                while self.running:
                    shake_cooldown = self._check_shake_logic(droid, name, shake_cooldown)
                    time.sleep(0.05)
                    
        except Exception as e:
            print(f"❌ [{name}] Connection/Runtime Error: {e}")
        finally:
            print(f"[{name}] Disconnected/Thread ending.")
            with self.lock:
                self.active_devices.discard(name)

    def _check_shake_logic(self, droid, name, current_cooldown):
        try:
            accel = droid.get_acceleration()
            if not accel:
                return current_cooldown

            x, y, z = accel["x"], accel["y"], accel["z"]
            magnitude = math.sqrt(x**2 + y**2 + z**2)

            if magnitude > SHAKE_THRESHOLD:
                now = time.time()
                if now > current_cooldown:
                    self.on_shake(name, magnitude)
                    return now + SHAKE_COOLDOWN
            
            return current_cooldown

        except Exception:
            return current_cooldown
            
    def on_shake(self, name, magnitude):
        print(f"🚀 [SHAKE DETECTED] Device: {name} | Intensity: {magnitude:.2f}")
        if self.on_shake_callback:
            self.on_shake_callback(name, magnitude)
    
    def stop(self):
        self.running = False


if __name__ == "__main__":
    controller = SpheroController(TARGET_SPHERO_NAMES)
    controller.start()