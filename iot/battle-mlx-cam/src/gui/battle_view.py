"""Battle View."""
import customtkinter as ctk
import threading
import time
import base64
from PIL import Image
from io import BytesIO

from src import Camera, list_cameras, transform_image, remove_background, get_api_key
from src.gui.components import CameraPreview, LogPanel
from src.config import PROMPT_MAPPING, KNN_DISTANCE_THRESHOLD, NON_RECOGNITION_LABELS, ATTACK_TO_COUNTER_LABEL

class BattlePanel:
    """Manages one side (Dream/Nightmare)."""
    def __init__(self, parent, role, title, color, view):
        self.role = role
        self.view = view
        self.camera = None
        self.cap_index = None
        
        # Frame
        self.frame = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=10)
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Title
        ctk.CTkLabel(self.frame, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=color).pack(pady=10)
        
        # Camera Select
        cam_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        cam_frame.pack(fill="x", padx=10)
        ctk.CTkLabel(cam_frame, text="Cam:", text_color="#888").pack(side="left")
        self.cam_var = ctk.StringVar(value="Select")
        self.cam_menu = ctk.CTkComboBox(cam_frame, variable=self.cam_var, command=self._on_cam_change)
        self.cam_menu.pack(side="left", fill="x", expand=True, padx=5)
        
        # Preview
        self.preview = CameraPreview(self.frame, height=220)
        self.preview.pack(fill="x", padx=10, pady=10)
        
        # Status
        self.rec_label = ctk.CTkLabel(self.frame, text="👁️ Scanning...", text_color="#666")
        self.rec_label.pack(anchor="w", padx=15)
        
        # Prompt
        self.prompt_entry = ctk.CTkEntry(self.frame, fg_color="#0f0f1a", border_color="#3d3d5c")
        self.prompt_entry.pack(fill="x", padx=10, pady=5)
        self.prompt_entry.insert(0, PROMPT_MAPPING.get("sword", "Steel katana sword cartoon style"))
        
        # Output
        ctk.CTkLabel(self.frame, text="🎨 Output", font=ctk.CTkFont(size=14, weight="bold"), text_color=color).pack(pady=(15,5))
        self.output = CameraPreview(self.frame, height=220, text="Waiting...")
        self.output.pack(fill="x", padx=10, pady=10)
        
        self.last_gen_time = 0

    def update_cameras(self, cams):
        if cams:
            opts = [f"{idx}: {name}" for idx, name in cams]
            self.cam_menu.configure(values=opts)
        else:
            self.cam_menu.configure(values=["No cameras"])
            
    def _on_cam_change(self, choice):
        try:
            idx = int(choice.split(':')[0])
            if self.camera: self.camera.close()
            self.camera = Camera(idx)
            self.camera.open()
            self.view.log(f"Cam {idx} assigned", "camera", self.role)
        except: pass

class BattleView(ctk.CTkFrame):
    """Main Battle Interface."""
    def __init__(self, parent, ws, knn, open_training_callback):
        super().__init__(parent, fg_color="#0a0a14")
        self.ws = ws
        self.knn = knn
        self.knn = knn
        self.open_training = open_training_callback
        self.running = False
        self.running = False
        self.current_attack = None
        self.attack_start_time = 0
        
        self._build_ui()
        self._detect_cameras()
        self._start_preview_loop()
        self._start_state_monitor()
        
    def _build_ui(self):
        # Top
        top = ctk.CTkFrame(self, height=40, fg_color="#1a1a2e")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="⚔️ BATTLE", font=ctk.CTkFont(size=18, weight="bold"), text_color="#a855f7").pack(side="left", padx=20)
        
        # Dataset Info
        self.ds_label = ctk.CTkLabel(top, text=f"📚 {self.knn.dataset_name} ({len(self.knn.training_samples)} samples)", text_color="#888")
        self.ds_label.pack(side="left", padx=20)
        
        ctk.CTkButton(top, text="🎓 Training", width=80, height=24, fg_color="#444", command=self.open_training).pack(side="right", padx=20, pady=8)
        
        # Main
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.panels = {
            'nightmare': BattlePanel(main, 'nightmare', "🌙 NIGHTMARE", "#ec4899", self),
            'dream': BattlePanel(main, 'dream', "☀️ DREAM", "#3b82f6", self)
        }
        
        # Logs
        log_frame = ctk.CTkFrame(main, width=280, fg_color="#1a1a2e")
        log_frame.pack(side="left", fill="y", padx=5)
        log_frame.pack_propagate(False)
        self.logger = LogPanel(log_frame)
        self.logger.pack(fill="both", expand=True)

        # Controls
        controls = ctk.CTkFrame(self, height=60, fg_color="#1a1a2e")
        controls.pack(fill="x")
        
        # Status Label instead of buttons
        self.status_label = ctk.CTkLabel(controls, text="⏳ WAITING FOR BATTLE STATE...", font=ctk.CTkFont(size=16, weight="bold"), text_color="#888")
        self.status_label.pack(pady=15)
        
        # self.start_btn = ctk.CTkButton(controls, text="▶ START ALL", font=ctk.CTkFont(size=16, weight="bold"), 
        #                                fg_color="#22c55e", width=180, height=40, command=self.start)
        # self.start_btn.pack(side="left", padx=20, pady=10)
        
        # self.stop_btn = ctk.CTkButton(controls, text="⏹ STOP", font=ctk.CTkFont(size=16, weight="bold"), 
        #                               fg_color="#ef4444", width=180, height=40, state="disabled", command=self.stop)
        # self.stop_btn.pack(side="left", padx=20)

    def log(self, msg, level="info", role=""):
        self.logger.log(msg, level, role)

    def _detect_cameras(self):
        cams = list_cameras()
        for p in self.panels.values():
            p.update_cameras(cams)

    def _start_preview_loop(self):
        for p in self.panels.values():
            if p.camera:
                p.preview.update_image(p.camera.capture())
        self.after(33, self._start_preview_loop)

    def start(self):
        if not get_api_key():
            self.log("FAL_KEY missing", "error")
            return
        self.running = True
        self.running = True
        # self.start_btn.configure(state="disabled")
        # self.stop_btn.configure(state="normal")
        self.log(f"Started (Attack: {self.current_attack})", "success")
        self._loop()

    def stop(self):
        self.running = False
        # self.start_btn.configure(state="normal")
        # self.stop_btn.configure(state="disabled")
        self.log("Stopped", "info")

    def _start_state_monitor(self):
        """Monitor server state to auto start/stop."""
        if self.ws.last_state:
            state = self.ws.last_state.get("battle_state", "IDLE")
            attack = self.ws.last_state.get("battle_boss_attack")
            
            if attack != self.current_attack:
                self.current_attack = attack
                self.attack_start_time = time.time()
                self.log(f"Boss Attack: {attack}", "info")
            
            # Auto Start/Stop
            if state == "FIGHTING" and not self.running:
                self.status_label.configure(text=f"⚔️ FIGHTING ({attack})", text_color="#22c55e")
                self.start()
            elif state in ["WEAKENED", "CAPTURED", "IDLE"] and self.running:
                self.status_label.configure(text=f"⏸ {state}", text_color="#ef4444")
                self.stop()
            elif not self.running:
                self.status_label.configure(text=f"⏳ {state}", text_color="#888")
            else:
                # Update label while running
                self.status_label.configure(text=f"⚔️ FIGHTING ({attack})", text_color="#22c55e")
                
        self.after(500, self._start_state_monitor)

    def _loop(self):
        if not self.running: return
        for role, p in self.panels.items():
            if p.camera:
                threading.Thread(target=self._process, args=(role, p), daemon=True).start()
        self.after(500, self._loop)

    def _process(self, role, p):
        try:
            frame = p.camera.capture()
            if not frame: return
            
            # DEMO MODE: Bypass KNN - directly use counter based on current_attack
            target_label = ATTACK_TO_COUNTER_LABEL.get(self.current_attack)
            
            if target_label:
                # Fake successful recognition for demo
                is_rec = True
                label = target_label
                
                # Update UI
                self.after(0, lambda l=label: p.rec_label.configure(
                    text=f"🎯 DEMO: {l.upper()}", text_color="#22c55e"
                ))
                
                # Set prompt from mapping
                new_prompt = PROMPT_MAPPING.get(label, f"{label} in cartoon style")
                if p.prompt_entry.get() != new_prompt:
                    self.after(0, lambda np=new_prompt: (
                        p.prompt_entry.delete(0, "end"), 
                        p.prompt_entry.insert(0, np)
                    ))
                self.log(f"Demo: Counter {label} for attack {self.current_attack}", "knn", role)
            else:
                # No attack defined, skip processing
                is_rec = False
                self.after(0, lambda: p.rec_label.configure(text="⏳ Waiting attack...", text_color="#666"))
                return

                return

            # Initial Delay: Wait 5s after attack starts before helping
            if time.time() - self.view.attack_start_time < 5.0:
                 self.after(0, lambda: p.rec_label.configure(text=f"⏳ Drawing time...", text_color="#eab308"))
                 return

            # Cost Control: Check if 3 seconds passed since last generation

            # Cost Control: Check if 3 seconds passed since last generation
            if time.time() - p.last_gen_time < 3.0:
                # Still transformed lately, skip expensive AI call
                return

            # 2. Transform
            prompt = p.prompt_entry.get()
            self.log("Transforming...", "ai", role)
            res, _ = transform_image(frame, prompt)
            
            # Update timestamp
            p.last_gen_time = time.time()
            
            # 3. BG
            final, _ = remove_background(res)
            self.after(0, lambda: p.output.update_image(final))
            
            # 4. WS
            b64 = base64.b64encode(final).decode('utf-8')
            extra = {f"battle_drawing_{role}_recognised": is_rec}
            if self.ws.send_image(b64, role, extra):
                self.log("Sent", "success", role)
                
        except Exception as e:
            self.log(f"Error: {e}", "error", role)
    
    def cleanup(self):
        self.running = False
        for p in self.panels.values():
            if p.camera: p.camera.close()
