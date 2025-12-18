import json
import logging
import threading
import time
import websocket
from queue import Queue, Empty
from controllerRaspberry import SpheroController, TARGET_SPHERO_NAMES

# ================= CONFIG =================
WS_URL = "ws://server.riftoperation.ethan-folio.fr/ws"
ROLE = "dream" # 'parent' or 'dream'
DEVICE_ID = "macbook_pro_1"

# Mock Config Factory since we don't have the files
class DepthConfigFactory:
    @staticmethod
    def create_default_parent():
        return type('Config', (), {
            'role': ROLE,
            'partitions': {
                # Map steps to sequences of Sphero Names
                # Example sequences. Adjust based on real game logic.
                1: ["SB-08C9", "SB-1219"], 
                2: ["SB-1219", "SB-08C9"],
                3: ["SB-08C9", "SB-08C9", "SB-1219"]
            },
            'button_pins': {}, 
            'led_pins': {}     
        })()

# ==========================================

class DepthController:
    def __init__(self):
        self.logger = logging.getLogger("DepthController")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        
        self.depthConfig = DepthConfigFactory.create_default_parent()
        self.role = self.depthConfig.role
        self.partitions = self.depthConfig.partitions
        self.state = {}
        self.is_playing = False
        self.device_id = DEVICE_ID
        self.last_log_time = 0
        
        # Helper for thread safety with WS
        self.ws_app = None
        self.ws_thread = None
        self.running = True
        
        # Sphero Integration
        self.shake_queue = Queue()
        self.sphero_controller = SpheroController(
            target_names=TARGET_SPHERO_NAMES,
            on_shake_callback=self.on_sphero_shake
        )

    def on_sphero_shake(self, name, magnitude):
        # Called from Sphero Thread
        self.shake_queue.put(name)

    # --------------------------------------------------
    # WebSocket Callbacks
    # --------------------------------------------------
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.state = data
            self.logger.info(f"📡 State updated: {json.dumps(data)}")
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON received: {message}")

    def on_error(self, ws, error):
        self.logger.error(f"[WS] Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info("[WS] Connection closed")

    def on_open(self, ws):
        self.logger.info("[WS] Connected!")

    def _run_ws(self):
        while self.running:
            self.logger.info(f"Connecting to {WS_URL}...")
            self.ws_app = websocket.WebSocketApp(
                WS_URL,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            # Blocking call, runs until connection closes
            self.ws_app.run_forever(ping_interval=60, ping_timeout=10)
            
            if self.running:
                self.logger.info("Reconnecting WS in 5s...")
                time.sleep(5)

    def send_state(self):
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            try:
                self.ws_app.send(json.dumps(self.state))
                self.logger.info("📤 State sent to Server")
            except Exception as e:
                self.logger.error(f"Failed to send state: {e}")

    # --------------------------------------------------
    # Conditions
    # --------------------------------------------------
    def depth_started(self):
        children_count = self.state.get("dream_rift_part_count", 0)
        parent_count = self.state.get("nightmare_rift_part_count", 0)
        started = children_count >= 1 and parent_count >= 1
        
        # Periodic logging for debugging wait state
        now = time.time()
        if not started and now - self.last_log_time > 5:
            self.logger.info(f"⏳ Waiting for start conditions... (ChildCount: {children_count}, ParentCount: {parent_count})")
            self.last_log_time = now
            
        return started

    def depth_finished(self):
        return (
            self.state.get("depth_step_3_nightmare_sucess") == True
            and self.state.get("depth_step_3_dream_sucess") == True
        )

    def current_step(self):
        for step in (1, 2, 3):
            key = f"depth_step_{step}_{self.role}_sucess"
            if self.state.get(key) is not True:
                return step
        return None

    # --------------------------------------------------
    # Gameplay
    # --------------------------------------------------
    def play_partition(self, sequence):
        self.logger.info(f"🎮 Starting partition: {sequence}")
        
        # Clear queue
        while not self.shake_queue.empty():
            try:
                self.shake_queue.get_nowait()
            except Empty:
                break

        index = 0
        while index < len(sequence):
            if not self.running:
                return False

            # Wait for a shake (blocking with timeout to allow exit check)
            try:
                self.logger.info(f"👉 Waiting for shake from: {sequence[index]}")
                shaken_sphero_name = self.shake_queue.get(timeout=1.0) 
            except Empty:
                continue

            expected = sequence[index]

            if shaken_sphero_name == expected:
                self.logger.info(f"✅ Correct Shake: {shaken_sphero_name} ({index + 1}/{len(sequence)})")
                index += 1
            else:
                self.logger.info(f"❌ Wrong Shake: {shaken_sphero_name} (Expected {expected}) -> RESET")
                index = 0

        self.logger.info("🎉 Partition Complete!")
        return True

    # --------------------------------------------------
    # Main Loop
    # --------------------------------------------------
    def run(self):
        # Start WS in background thread
        self.ws_thread = threading.Thread(target=self._run_ws, daemon=True)
        self.ws_thread.start()

        # Start Sphero Controller in background (it launches its own threads)
        self.sphero_controller.start()

        try:
            while self.running:
                self.game_logic()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Stopping...")
        finally:
            self.running = False
            self.sphero_controller.stop()
            if self.ws_app:
                self.ws_app.close()

    def game_logic(self):
        if not self.depth_started():
            time.sleep(0.1)
            return

        if self.is_playing:
            return

        step = self.current_step()
        if step is None or step > 3:
            return

        # Synchronization Logic
        if self.role == "dream" and step > 1:
            parent_prev_key = f"depth_step_{step - 1}_nightmare_sucess"
            if self.state.get(parent_prev_key) is not True:
                # Periodic log for step wait?
                # self.logger.info(f"⏳ Waiting for Parent Step {step-1}")
                return

        partition = self.partitions.get(step)
        if not partition:
            return

        self.is_playing = True
        self.logger.info(f"🚀 {self.role.upper()} Playing Step {step}")

        # Play the actual game (blocking logic is fine here as WS is in thread)
        success = self.play_partition(partition)
        
        if success:
            key = f"depth_step_{step}_{self.role}_sucess"
            self.state[key] = True
            self.send_state()

            if self.depth_finished():
                self.logger.info("🏁 DEPTH FINISHED!")
                self.send_state()

        self.is_playing = False

if __name__ == "__main__":
    controller = DepthController()
    controller.run()
