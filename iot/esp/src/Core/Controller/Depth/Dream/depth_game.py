import json
import logging
import threading
import time
import websocket
from queue import Queue, Empty
from controllerRaspberry import SpheroController, TARGET_SPHERO_NAMES

# ================= CONFIG =================
WS_URL = "ws://192.168.10.7:8000/ws"
ROLE = "dream"
DEVICE_ID = "macbook_pro_1"

# ==========================================

class DepthController:
    def __init__(self):
        self.logger = logging.getLogger("DepthController")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        
        self.role = ROLE
        self.state = {
            "depth_current_player": "dream",
            "depth_partition": [1, 2, 3, 4, 5, 6, 5, 4, 5, 1, 3, 2, 2, 3, 1, 2, 5, 6, 4, 5],
            "depth_partition_position": 0
        }
        self.is_playing = False
        self.device_id = DEVICE_ID
        self.last_log_time = 0
        self.partition_started = False  # Only gate the very first note
        
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
        
        # Mapping Sphero -> Note (1-3 pour dream)
        self.sphero_to_note = {
            "SB-08C9": 1,  # DO
            "SB-1219": 2,  # RE
            "SB-2020": 3   # MI
        }
        
        # Mapping Note -> Sound name
        self.note_to_sound = {
            1: "DO",
            2: "RE",
            3: "MI",
        }

    def on_sphero_shake(self, name, magnitude):
        # Called from Sphero Thread
        self.shake_queue.put(name)

    # --------------------------------------------------
    # Helper Functions
    # --------------------------------------------------
    
    def get_role_for_note(self, note):
        """Détermine qui doit jouer cette note"""
        if 1 <= note <= 3:
            return "dream"
        elif 4 <= note <= 6:
            return "nightmare"
        return None
    
    def is_my_turn(self):
        """Vérifie si c'est notre tour de jouer"""
        current_player = self.state.get("depth_current_player")
        partition = self.state.get("depth_partition", [])
        position = self.state.get("depth_partition_position", 0)
        
        if current_player != self.role:
            return False
        
        if position >= len(partition):
            return False
        
        current_note = partition[position]
        expected_role = self.get_role_for_note(current_note)
        
        return expected_role == self.role

    # --------------------------------------------------
    # WebSocket Callbacks
    # --------------------------------------------------
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            # Only update values that are not None (preserve defaults)
            for key, value in data.items():
                if value is not None:
                    self.state[key] = value
            self.logger.info(f"📡 State updated: {json.dumps(self.state)}")
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

    def play_note(self, note):
        note_string = self.note_to_sound.get(note)
        if note_string:
            note_json = {"depth_note": note_string}
            if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
                try:
                    self.ws_app.send(json.dumps(note_json))
                    self.logger.info(f"🎵 Playing note: {note_string} (note {note})")
                except Exception as e:
                    self.logger.error(f"Failed to send note: {e}")

    def play_sound(self, name):
        sound_json = {"depth_sound": name}
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            try:
                self.ws_app.send(json.dumps(sound_json))
                self.logger.info(f"🎵 Playing sound: {name}")
            except Exception as e:
                self.logger.error(f"Failed to send sound: {e}")
    
    def play_note_sound(self, note):
        note_string = self.note_to_sound.get(note)
        sound_json = {"depth_sound": note_string}
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            try:
                self.ws_app.send(json.dumps(sound_json))
                self.logger.info(f"🎵 Playing sound: {note}")
            except Exception as e:
                self.logger.error(f"Failed to send sound: {e}")

    # --------------------------------------------------
    # Conditions
    # --------------------------------------------------
    def depth_started(self):
        rift_part_count = self.state.get("rift_part_count", 0)
        started = rift_part_count == 2
        
        # Periodic logging for debugging wait state
        now = time.time()
        if not started and now - self.last_log_time > 5:
            self.logger.info(f"⏳ Waiting for start conditions... (RiftPartCount: {rift_part_count})")
            self.last_log_time = now
            
        return started

    def depth_finished(self):
        partition = self.state.get("depth_partition", [])
        position = self.state.get("depth_partition_position", 0)
        return position >= len(partition)

    # --------------------------------------------------
    # Gameplay
    # --------------------------------------------------
    
    def wait_for_start_shake(self):
        """Attend un shake quelconque pour lancer la partition (ne compte pas comme note)"""
        self.logger.info("⏳ Waiting for any shake to START the game...")
        
        # Clear queue
        while not self.shake_queue.empty():
            try:
                self.shake_queue.get_nowait()
            except Empty:
                break
        
        # Wait for any shake
        while True:
            if self.state.get("reset_system"):
                return False
            if not self.running:
                return False
            
            try:
                shaken_sphero = self.shake_queue.get(timeout=1.0)
                self.logger.info(f"🚀 Start shake received from {shaken_sphero} - GAME BEGINS!")
                # Send a special "start" signal (not a note)
                start_json = {"depth_game_started": True}
                if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
                    self.ws_app.send(json.dumps(start_json))
                self.partition_started = True
                return True
            except Empty:
                continue
    
    def play_partition(self):
        """Joue la partie de la partition qui nous revient (ping-pong)"""
        partition = self.state.get("depth_partition", [])
        position = self.state.get("depth_partition_position", 0)
        
        self.logger.info(f"🎮 Starting my turn at position {position}")
        
        # Clear queue
        while not self.shake_queue.empty():
            try:
                self.shake_queue.get_nowait()
            except Empty:
                break

        while position < len(partition):
            current_note = partition[position]
            expected_role = self.get_role_for_note(current_note)
            
            # Si ce n'est plus notre tour, on arrête et on passe la main
            if expected_role != self.role:
                self.logger.info(f"🔄 Changement de rôle -> {expected_role}")
                self.state["depth_current_player"] = expected_role
                self.state["depth_partition_position"] = position
                self.send_state()
                return True
            
            # 🛑 Check Reset
            if self.state.get("reset_system"):
                self.logger.info("🔄 Reset triggered during game!")
                return False

            if not self.running:
                return False

            # Wait for a shake (blocking with timeout to allow exit check)
            try:
                self.logger.info(f"👉 Waiting for Sphero shake for note {current_note} (position {position})")
                shaken_sphero_name = self.shake_queue.get(timeout=1.0)
            except Empty:
                continue

            # Convertir le sphero secoué en note
            shaken_note = self.sphero_to_note.get(shaken_sphero_name)
            
            self.logger.info(f"🎯 Sphero secoué: {shaken_sphero_name} -> Note: {shaken_note} | Note attendue: {current_note}")
            
            # Always send the note that was actually played
            self.play_note(shaken_note)
            self.play_note_sound(shaken_note)
            
            if shaken_note == current_note:
                self.logger.info(f"✅ Correct Shake: {shaken_sphero_name} = note {shaken_note} ({position + 1}/{len(partition)})")
                position += 1
                self.state["depth_partition_position"] = position
            else:
                # Wrong shake - note already sent, now play false sound and RETRY
                time.sleep(1.0)
                self.play_sound("false")
                self.logger.info(f"❌ Wrong Shake: Sphero {shaken_sphero_name} (note {shaken_note}) != attendu note {current_note} -> RETRY to first note")
                position = 0
                self.state["depth_partition_position"] = position
                # Continue playing from first note (don't return, just loop back)

        # Partition terminée !
        self.play_sound("correct")
        self.state["depth_partition_position"] = position
        self.send_state()
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
        # 0. Check Reset System
        if self.state.get("reset_system") is True:
            if self.is_playing:
                self.is_playing = False
            if self.partition_started:
                self.partition_started = False
                self.logger.info("🔄 Reset active - Pausing system")
            time.sleep(1)
            return

        if not self.depth_started():
            time.sleep(0.1)
            return

        if self.is_playing:
            return

        # Check if game is finished
        if self.depth_finished():
            return

        # Check if it's our turn
        if not self.is_my_turn():
            # Periodic log
            now = time.time()
            if now - self.last_log_time > 3:
                current_player = self.state.get("depth_current_player", "?")
                self.logger.info(f"⏳ Waiting for our turn... (current player: {current_player})")
                self.last_log_time = now
            return

        self.is_playing = True
        self.logger.info(f"🚀 {self.role.upper()} Playing!")

        # 1. Wait for a shake to START the partition (only once at very beginning)
        if not self.partition_started and self.state.get("depth_partition_position", 0) == 0:
            started = self.wait_for_start_shake()
            if not started:
                self.is_playing = False
                return
        
        # 2. Play the actual partition (handles RETRY internally by looping back to first note)
        result = self.play_partition()
        
        if result == True:
            # Success - check if finished
            if self.depth_finished():
                self.logger.info("🏁 DEPTH FINISHED!")
                self.state["depth_state"] = "complete"
                self.send_state()

        self.is_playing = False

if __name__ == "__main__":
    controller = DepthController()
    controller.run()
