"""Headless Battle Service - Core battle logic without GUI."""
import threading
import time
import base64

from src import Camera, list_cameras, transform_image, remove_background, get_api_key, KNNService, RiftWebSocket
from src.config import PROMPT_MAPPING, ATTACK_TO_COUNTER_LABEL


class CameraPanel:
    """Manages one camera (Dream/Nightmare)."""
    def __init__(self, role: str, camera_index: int = None):
        self.role = role
        self.camera = None
        self.camera_index = camera_index
        self.last_gen_time = 0
        self.last_frame = None
        self.last_output = None
        self.recognition_status = "Waiting..."
        self.prompt = PROMPT_MAPPING.get("sword", "Steel katana sword cartoon style")
        
        if camera_index is not None:
            self.set_camera(camera_index)
    
    def set_camera(self, index: int) -> bool:
        """Set camera by index."""
        try:
            if self.camera:
                self.camera.close()
            self.camera = Camera(index)
            self.camera.open()
            self.camera_index = index
            print(f"[BattleService] {self.role} camera set to {index}")
            return True
        except Exception as e:
            print(f"[BattleService] Failed to set {self.role} camera: {e}")
            return False
    
    def capture(self) -> bytes:
        """Capture frame from camera."""
        if self.camera:
            self.last_frame = self.camera.capture()
            return self.last_frame
        return None
    
    def close(self):
        """Close camera."""
        if self.camera:
            self.camera.close()
            self.camera = None


class BattleService:
    """Headless battle service managing cameras, KNN, and WebSocket."""
    
    def __init__(self, nightmare_cam: int = 0, dream_cam: int = 1):
        # Cameras
        self.panels = {
            'nightmare': CameraPanel('nightmare', nightmare_cam),
            'dream': CameraPanel('dream', dream_cam)
        }
        
        # Services
        self.knn = KNNService(dataset_name="default_dataset")
        self.ws = RiftWebSocket()
        
        # State
        self.running = False
        self.current_attack = None
        self.attack_start_time = 0
        
        # Connect to WebSocket
        self.ws.connect()
        
        print("[BattleService] Initialized")
    
    def get_status(self) -> dict:
        """Get current status."""
        return {
            "running": self.running,
            "current_attack": self.current_attack,
            "ws_connected": self.ws.connected if self.ws else False,
            "ws_state": self.ws.last_state,
            "cameras": {
                role: {
                    "index": p.camera_index,
                    "has_camera": p.camera is not None,
                    "recognition": p.recognition_status
                }
                for role, p in self.panels.items()
            }
        }
    
    def set_camera(self, role: str, index: int) -> bool:
        """Set camera for a role."""
        if role in self.panels:
            return self.panels[role].set_camera(index)
        return False
    
    def start(self):
        """Start battle processing."""
        if not get_api_key():
            print("[BattleService] FAL_KEY missing - continuing without AI transform")
        
        self.running = True
        print("[BattleService] Started")
        
        # Start preview capture thread (always runs for config page)
        self._preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self._preview_thread.start()
        
        # Start processing thread (for AI transforms)
        self._process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._process_thread.start()
        
        # Start state monitor
        self._monitor_thread = threading.Thread(target=self._state_monitor, daemon=True)
        self._monitor_thread.start()
        
        return True
    
    def _preview_loop(self):
        """Capture frames for preview (5 FPS)."""
        while self.running:
            for role, panel in self.panels.items():
                try:
                    if panel.camera:
                        panel.capture()
                except Exception as e:
                    print(f"[BattleService] Preview capture error {role}: {e}")
            time.sleep(0.2)  # 5 FPS
    
    def stop(self):
        """Stop battle processing."""
        self.running = False
        print("[BattleService] Stopped")
    
    def _state_monitor(self):
        """Monitor WebSocket state for auto start/stop."""
        while True:
            if self.ws.last_state:
                state = self.ws.last_state.get("battle_state", "IDLE")
                attack = self.ws.last_state.get("battle_boss_attack")
                
                if attack != self.current_attack:
                    self.current_attack = attack
                    self.attack_start_time = time.time()
                    print(f"[BattleService] Boss Attack: {attack}")
            
            time.sleep(0.5)
    
    def _process_loop(self):
        """Main processing loop."""
        while self.running:
            for role, panel in self.panels.items():
                if panel.camera:
                    threading.Thread(
                        target=self._process_panel, 
                        args=(role, panel), 
                        daemon=True
                    ).start()
            time.sleep(0.5)
    
    def _process_panel(self, role: str, panel: CameraPanel):
        """Process a single panel."""
        try:
            frame = panel.capture()
            if not frame:
                return
            
            # Wait 5s after attack starts
            if self.current_attack and (time.time() - self.attack_start_time < 5.0):
                remaining = 5.0 - (time.time() - self.attack_start_time)
                panel.recognition_status = f"⏳ Drawing time... ({remaining:.1f}s)"
                return
            
            # Demo mode: use counter based on attack
            target_label = ATTACK_TO_COUNTER_LABEL.get(self.current_attack)
            is_rec = False
            
            if target_label:
                is_rec = True
                label = target_label
                panel.recognition_status = f"🎯 DEMO: {label.upper()}"
                panel.prompt = PROMPT_MAPPING.get(label, f"{label} in cartoon style")
            else:
                panel.recognition_status = "⏳ Waiting attack..."
                return
            
            # Rate limit: 3s between generations
            if time.time() - panel.last_gen_time < 3.0:
                return
            
            # Transform image
            print(f"[BattleService] Transforming {role}...")
            res, _ = transform_image(frame, panel.prompt)
            panel.last_gen_time = time.time()
            
            # Remove background
            final, _ = remove_background(res)
            panel.last_output = final
            
            # Send via WebSocket
            b64 = base64.b64encode(final).decode('utf-8')
            extra = {f"battle_drawing_{role}_recognised": is_rec}
            if self.ws.send_image(b64, role, extra):
                print(f"[BattleService] Sent {role}")
                
        except Exception as e:
            print(f"[BattleService] Error processing {role}: {e}")
            panel.recognition_status = f"❌ Error: {e}"
    
    def cleanup(self):
        """Cleanup resources."""
        self.running = False
        for panel in self.panels.values():
            panel.close()
        self.ws.close()
        print("[BattleService] Cleaned up")


# Global instance
_service: BattleService = None

def get_service() -> BattleService:
    """Get the singleton BattleService instance."""
    global _service
    return _service

def init_service(nightmare_cam: int = 0, dream_cam: int = 1) -> BattleService:
    """Initialize the BattleService singleton."""
    global _service
    _service = BattleService(nightmare_cam, dream_cam)
    return _service
