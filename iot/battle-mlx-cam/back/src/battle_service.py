"""Headless Battle Service - Core battle logic without GUI."""
import threading
import time
import base64

from src import transform_image, remove_background, get_api_key, KNNService, RiftWebSocket, list_cameras
from src.config import PROMPT_MAPPING, ATTACK_TO_COUNTER_LABEL

# Configurable rate limit between AI generations (per role)
GENERATION_RATE_LIMIT_S = 2.0  # 2 seconds between generations

# We need socketio to emit back 'output_frame' to the frontend client who sent it
# But BattleService doesn't have direct access to socketio object usually.
# The web_server calls service.process_client_frame.
# The service should probably return the result or use a callback?
# The original code used socketio.emit in web_server.py's _broadcast_loop reading from panel.last_output.
# We can keep a similar pattern: service updates state, and web_server broadcasts update events.
# Or better: service emits event directly via a callback provided at init.

class BattleRoleState:
    """Manages state for one role (Dream/Nightmare)."""
    def __init__(self, role: str):
        self.role = role
        self.last_gen_time = 0
        self.last_output = None # Bytes of the PNG output
        self.recognition_status = "Waiting..."
        self.last_label = None
        self.prompt = PROMPT_MAPPING.get("sword", "Steel katana sword cartoon style")
        self.processing = False

class BattleService:
    """Headless battle service managing AI processing and WebSocket."""
    
    def __init__(self):
        # Roles
        self.roles = {
            'nightmare': BattleRoleState('nightmare'),
            'dream': BattleRoleState('dream')
        }
        
        # Services
        self.knn = KNNService(dataset_name="default_dataset")
        self.ws = RiftWebSocket()
        
        # State
        self.running = False
        self.current_attack = None
        self.attack_start_time = 0
        self.socketio = None # Set later
        
        # Connect to WebSocket to Rift Server
        self.ws.connect()
        
        print("[BattleService] Initialized (Client-Side Camera Mode)")
    
    def set_socketio(self, socketio):
        self.socketio = socketio

    def get_status(self) -> dict:
        """Get current status."""
        return {
            "running": self.running,
            "current_attack": self.current_attack,
            "ws_connected": self.ws.connected if self.ws else False,
            "ws_state": self.ws.last_state,
            "cameras": {
                role: {
                    "recognition": p.recognition_status,
                    "label": p.last_label,
                    "processing": p.processing
                }
                for role, p in self.roles.items()
            }
        }
    
    # Legacy for web_server compatibility
    def set_camera(self, role: str, index: int) -> bool:
        return True 

    @property
    def panels(self):
        # Compatibility property for old code accessing service.panels.items()
        # We simulate objects with expected attributes if needed, or just return roles
        # The old code accessed panel.camera and panel.last_frame/output
        # We need to adapt web_server.py to not rely on this property for broadcasting camera frames anymore.
        return self.roles

    def start(self):
        """Start battle processing."""
        if not get_api_key():
            print("[BattleService] FAL_KEY missing - continuing without AI transform")
        
        self.running = True
        print("[BattleService] Started")
        
        # Start state monitor
        self._monitor_thread = threading.Thread(target=self._state_monitor, daemon=True)
        self._monitor_thread.start()
        
        return True
    
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
                    # Broadcast status update via socketio
                    if self.socketio:
                        self.socketio.emit('status', self.get_status())
            
            time.sleep(0.5)

    def process_client_frame(self, role: str, image_bytes: bytes):
        """Process a frame received from a client."""
        if role not in self.roles:
            return
            
        state = self.roles[role]
        
        # Rate limit (configurable at top of file)
        if time.time() - state.last_gen_time < GENERATION_RATE_LIMIT_S:
            return # Skip silently
        
        if state.processing:
            return

        # Start async processing
        state.processing = True
        state.last_gen_time = time.time()
        
        threading.Thread(
            target=self._process_image_task,
            args=(role, state, image_bytes),
            daemon=True
        ).start()

    def _process_image_task(self, role: str, state: BattleRoleState, image_bytes: bytes):
        try:
            # 1. Determine Prompt based on Game State
            # Wait 5s after attack starts? (Game logic)
            if self.current_attack and (time.time() - self.attack_start_time < 5.0):
                remaining = 5.0 - (time.time() - self.attack_start_time)
                state.recognition_status = f"⏳ Drawing time... ({remaining:.1f}s)"
                self._emit_status()
                return

            # Demo/Game Logic: Target label based on Current Attack
            target_label = ATTACK_TO_COUNTER_LABEL.get(self.current_attack)
            
            if target_label:
                # We assume player is drawing the counter
                # In real game we would use KNN to recognize drawing
                # Here we just assume and generate that item
                label = target_label
                state.last_label = label
                state.recognition_status = f"🎯 DEMO: {label.upper()}"
                state.prompt = PROMPT_MAPPING.get(label, f"{label} in cartoon style")
            else:
                state.recognition_status = "⏳ Waiting attack..."
                state.last_label = None
                self._emit_status()
                return

            self._emit_status()

            # 2. Transform Image (AI)
            print(f"[BattleService] Transforming {role}...")
            # We need to decode bytes to numpy/cv2 for transform_image? 
            # transform_image expects PIL Image or bytes?
            # It expects PIL Image usually or cv2 array. Let's check src/__init__.py or transform.py
            # Assuming transform_image handles bytes or we convert securely.
            # Let's decode to be safe if needed, but transform.py usually takes PIL.
            
            from PIL import Image
            import io
            import numpy as np
            import cv2
            
            img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_cv2 = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            res, _ = transform_image(img_cv2, state.prompt)
            
            # 3. Remove Background
            final_bytes, _ = remove_background(res)
            
            state.last_output = final_bytes
            
            # 4. Emit Result back to Frontend
            if self.socketio:
                b64 = base64.b64encode(final_bytes).decode('utf-8')
                self.socketio.emit('output_frame', {
                    'role': role,
                    'frame': b64
                })
            
            # 5. Send to Rift Server
            # We send bytes base64 encoded
            b64_rift = base64.b64encode(final_bytes).decode('utf-8')
            extra = {f"battle_drawing_{role}_recognised": True}
            if self.ws.send_image(b64_rift, role, extra):
                print(f"[BattleService] Sent {role} to Rift Server")

        except Exception as e:
            print(f"[BattleService] Error processing {role}: {e}")
            state.recognition_status = f"❌ Error: {e}"
        finally:
            state.processing = False
            self._emit_status()

    def _emit_status(self):
        if self.socketio:
            self.socketio.emit('status', self.get_status())

    def cleanup(self):
        """Cleanup resources."""
        self.running = False
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
    _service = BattleService() # No params needed anymore
    return _service
