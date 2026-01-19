"""Headless Battle Service - Core battle logic using State Pattern."""
import threading
import time
import base64
from typing import Optional

from ..Config import Config
from ..Network.RiftWebSocket import RiftWebSocket
from ..Utils import ImageProcessor, ProcessingResult

from .BattleState.BattleState import BattleState
from .BattleState.IdleState import IdleState

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

class BattleService:
    """Headless battle service managing AI processing and WebSocket."""
    
    def __init__(self):
        self.roles = {
            'nightmare': BattleRoleState('nightmare'),
            'dream': BattleRoleState('dream')
        }
        
        self.processor = ImageProcessor()
        self.ws = RiftWebSocket()
        
        self.running = False
        self.socketio = None
        
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
                    "processing": p.processing
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
            print(f"[BattleService] ⚙️ Processing task for {role}...")
            
            # Delegate to Current State
            result = self.state.process_frame(role, image_bytes)
            
            if not result:
                state.recognition_status = "Skipped (State)"
                return

            # Update State
            state.knn_label = result.label
            state.knn_distance = result.distance
            state.last_label = result.label
            state.recognition_status = result.status_message
            state.prompt = result.prompt
            
            self._emit_status()
            
            if result.should_skip:
                return

            if result.output_image:
                # Emit Output to Frontend
                if self.socketio:
                    b64 = base64.b64encode(result.output_image).decode('utf-8')
                    self.socketio.emit('output_frame', {
                        'role': role,
                        'frame': b64
                    })
                
                # Send to Rift Server
                b64_rift = base64.b64encode(result.output_image).decode('utf-8')
                extra = {f"battle_drawing_{role}_recognised": result.is_valid_counter}
                
                # Proxy Send
                if self.ws.send_image(b64_rift, role, extra):
                    print(f"[BattleService] Sent {role} to Rift Server (valid: {result.is_valid_counter})")

        except Exception as e:
            print(f"[BattleService] Error processing {role}: {e}")
            state.recognition_status = "❌ Error"
        finally:
            state.processing = False
            print(f"[BattleService] ✅ Task finished for {role}")
            self._emit_status()

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
