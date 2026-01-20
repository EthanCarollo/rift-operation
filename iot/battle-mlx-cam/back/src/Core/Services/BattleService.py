"""Headless Battle Service - Core battle logic using State Pattern."""
import threading
import time
import base64
import io
from PIL import Image
from typing import Optional

from ..Config import Config
from ..Network.RiftWebSocket import RiftWebSocket
from ..Utils import ImageProcessor, ProcessingResult
from ..Recognition.KNNRecognizer import KNNRecognizer

from .BattleState.BattleState import BattleState
from .BattleState.IdleState import IdleState
from .BattleState.AppearingState import AppearingState
from .BattleState.FightingState import FightingState
from .BattleState.HitState import HitState
from .BattleState.WeakenedState import WeakenedState
from .BattleState.CapturedState import CapturedState

# --- Constants ---
GENERATION_RATE_LIMIT_S = 2.0
INITIAL_HP = 5

class BattleRoleState:
    """Manages state for one role (Dream/Nightmare)."""
    def __init__(self, role: str):
        self.role = role
        self.last_gen_time = 0
        self.recognition_status = "Waiting..."
        self.last_label = None
        self.prompt = None
        self.processing = False
        
        # New result fields
        self.knn_label = None
        self.knn_distance = None
        
        # Crop settings (x, y, w, h) normalized
        self.crop = None
        # Rotation in degrees (0, 90, 180, 270)
        self.rotation = 0
        # Grayscale (black & white) filter
        self.grayscale = False

class BattleService:
    """Headless battle service managing AI processing and WebSocket."""
    
    def __init__(self):
        self.roles = {
            'nightmare': BattleRoleState('nightmare'),
            'dream': BattleRoleState('dream')
        }
        
        self.processor = ImageProcessor()
        self.ws = RiftWebSocket()
        self.knn = KNNRecognizer()
        
        self.running = False
        self.socketio = None

        # State tracking for edge detection
        self.last_hit_confirmed = False
        
        # Game State
        self.current_hp = INITIAL_HP
        self.current_attack = None
        self.state: BattleState = IdleState(self) # Initial State
        
        self.ws.connect()
        print("[BattleService] Initialized (State Pattern / Services)")
    
    def set_socketio(self, socketio):
        self.socketio = socketio

    def change_state(self, new_state: BattleState):
        """Transition to a new state."""
        self.state = new_state
        self.state.enter()

    def get_status(self) -> dict:
        return {
            "running": self.running,
            "current_attack": self.current_attack,
            "current_hp": self.current_hp,
            "battle_state": type(self.state).__name__.replace("State", "").upper(), # IDLE, FIGHTING...
            "ws_connected": self.ws.connected if self.ws else False,
            "ws_state": self.ws.last_state,
            "cameras": {
                role: {
                    "recognition": p.recognition_status,
                    "label": p.last_label,
                    "knn_label": p.knn_label,
                    "knn_distance": p.knn_distance,
                    "processing": p.processing,
                    "crop": p.crop,
                    "rotation": p.rotation,
                    "grayscale": p.grayscale
                }
                for role, p in self.roles.items()
            }
        }

    def start(self):
        if not Config.get_api_key():
            print("[BattleService] FAL_KEY missing - AI will fail")
        
        self.running = True
        print("[BattleService] Started")
        
        # Enter initial state
        self.state.enter()
        
        self._monitor_thread = threading.Thread(target=self._state_monitor, daemon=True)
        self._monitor_thread.start()
        return True
    
    def stop(self):
        self.running = False
        print("[BattleService] Stopped")
    
    def _state_monitor(self):
        while self.running:
            # Delegate to current state
            self.state.handle_monitor()
            time.sleep(0.5)

    def process_client_frame(self, role: str, image_bytes: bytes):
        if not self.running or role not in self.roles:
            return
            
        state = self.roles[role]
        
        # Apply crop if exists
        if state.crop:
            print(f"[BattleService] Applying crop for {role}: {state.crop}")
            try:
                img = Image.open(io.BytesIO(image_bytes))
                original_size = img.size
                w, h = img.size
                left = int(state.crop['x'] * w)
                top = int(state.crop['y'] * h)
                width = int(state.crop['w'] * w)
                height = int(state.crop['h'] * h)
                
                if width > 0 and height > 0:
                    img = img.crop((left, top, left + width, top + height))
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG')
                    image_bytes = buf.getvalue()
                    print(f"[BattleService] Crop applied for {role}: {original_size} -> {img.size}")
                else:
                    print(f"[BattleService] Invalid crop dimensions for {role}: width={width}, height={height}")
            except Exception as e:
                print(f"[BattleService] Crop failed for {role}: {e}")
        else:
            # Log only occasionally to avoid spam
            if not hasattr(state, '_crop_warned'):
                print(f"[BattleService] No crop configured for {role}")
                state._crop_warned = True
        
        # Apply rotation if set
        if state.rotation and state.rotation != 0:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                # PIL rotate is counter-clockwise, so we negate for clockwise rotation
                # Also, expand=True ensures the image is resized to fit the rotated content
                if state.rotation == 90:
                    img = img.transpose(Image.ROTATE_270)  # 90° clockwise
                elif state.rotation == 180:
                    img = img.transpose(Image.ROTATE_180)
                elif state.rotation == 270:
                    img = img.transpose(Image.ROTATE_90)   # 270° clockwise = 90° counter-clockwise
                
                buf = io.BytesIO()
                img.save(buf, format='JPEG')
                image_bytes = buf.getvalue()
                print(f"[BattleService] Rotation {state.rotation}° applied for {role}")
            except Exception as e:
                print(f"[BattleService] Rotation failed for {role}: {e}")
        
        # Apply grayscale (black & white) if enabled
        if state.grayscale:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                # Convert to grayscale then back to RGB (for consistent format)
                img = img.convert('L').convert('RGB')
                buf = io.BytesIO()
                img.save(buf, format='JPEG')
                image_bytes = buf.getvalue()
                print(f"[BattleService] Grayscale applied for {role}")
            except Exception as e:
                print(f"[BattleService] Grayscale failed for {role}: {e}")
        
        # DEBUG: Emit the actual image being processed (cropped + rotated + grayscale)
        if self.socketio:
            encoded_crop = base64.b64encode(image_bytes).decode('utf-8')
            self.socketio.emit('debug_cropped_frame', {'role': role, 'frame': encoded_crop})

        if time.time() - state.last_gen_time < GENERATION_RATE_LIMIT_S:
            return
        
        if state.processing:
            return

        state.processing = True
        state.last_gen_time = time.time()
        
        threading.Thread(
            target=self._process_image_task,
            args=(role, state, image_bytes),
            daemon=True
        ).start()

    def _process_image_task(self, role: str, state: BattleRoleState, image_bytes: bytes):
        try:
            # Delegate entirely to the Current State
            self.state.on_image_task(role, state, image_bytes)
        except Exception as e:
            print(f"[BattleService] Error in task wrapper: {e}")
        finally:
            state.processing = False
            self._emit_status()

    def update_role_crop(self, role: str, crop: dict):
        """Update crop settings for a role."""
        if role in self.roles:
            self.roles[role].crop = crop
            # Reset the crop warning flag when crop is updated
            if hasattr(self.roles[role], '_crop_warned'):
                delattr(self.roles[role], '_crop_warned')
            print(f"[BattleService] Updated crop for {role}: {crop}")
            self._emit_status()

    def update_role_rotation(self, role: str, rotation: int):
        """Update rotation settings for a role (0, 90, 180, 270)."""
        if role in self.roles:
            # Validate rotation value
            if rotation not in [0, 90, 180, 270]:
                rotation = 0
            self.roles[role].rotation = rotation
            print(f"[BattleService] Updated rotation for {role}: {rotation}°")
            self._emit_status()

    def update_role_grayscale(self, role: str, enabled: bool):
        """Update grayscale (black & white) setting for a role."""
        if role in self.roles:
            self.roles[role].grayscale = bool(enabled)
            print(f"[BattleService] Updated grayscale for {role}: {enabled}")
            self._emit_status()

    def force_end_fight(self):
        """Manually force end the fight and reset to Idle."""
        print("[BattleService] 🛑 Force End Fight triggered by operator")
        self.current_hp = INITIAL_HP
        self.current_attack = None
        
        # Reset roles? Maybe
        # self.roles['nightmare'].processing = False
        # self.roles['dream'].processing = False
        
        self.change_state(IdleState(self))
        self.broadcast_state("IDLE")

    def force_start_fight(self):
        """Manually force start the fight."""
        print("[BattleService] ⚔️ Force Start Fight triggered by operator")
        self.change_state(AppearingState(self))

    def broadcast_state(self, state_name: str, payload: dict = None):
        """Helper to broadcast state changes to Frontend and Rift."""
        data = {
            "battle_state": state_name,
            "battle_boss_hp": self.current_hp,
            "battle_boss_attack": self.current_attack
        }
        if payload:
            data.update(payload)
            
        # 1. Send to Frontend
        if self.socketio:
            self.socketio.emit('status', self.get_status())
            self.socketio.emit('battle_state_update', data) # Explicit event might be useful
            
        # 2. Send to Rift (Proxy)
        self.ws.send_raw(data)

    def _emit_status(self):
        if self.socketio:
            self.socketio.emit('status', self.get_status())

    def cleanup(self):
        self.running = False
        self.ws.close()
        print("[BattleService] Cleaned up")

# Global instance
_service: BattleService = None

def get_service() -> BattleService:
    global _service
    return _service

def init_service(nightmare_cam: int = 0, dream_cam: int = 1) -> BattleService:
    global _service
    _service = BattleService()
    return _service
