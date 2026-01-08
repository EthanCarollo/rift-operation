#!/usr/bin/env python3
"""
Battle Camera - Transform webcam drawings into AI art
Dual-Panel UI for Dream and Nightmare
With KNN Object Recognition
"""

import base64
import threading
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

import customtkinter as ctk

# Load .env file
load_dotenv()

# Import our modules
from src import Camera, list_cameras, transform_image, get_api_key, remove_background, RiftWebSocket, KNNService


# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Panel:
    """Class to manage one side (Dream or Nightmare)."""
    
    def __init__(self, parent, role, title, color, app):
        self.role = role
        self.color = color
        self.app = app
        self.camera = None
        self.cap_index = None
        
        # Main Frame
        self.frame = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=10)
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Title
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color
        ).pack(side="left", padx=10)
        
        # Training Button (Small)
        self.train_btn = ctk.CTkButton(
            title_frame, text="🎓 Train", width=60, height=24,
            fg_color="#444", font=ctk.CTkFont(size=11),
            command=self.open_train_dialog
        )
        self.train_btn.pack(side="right", padx=10)
        
        # --- Camera Section ---
        cam_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        cam_frame.pack(fill="x", padx=10)
        
        ctk.CTkLabel(cam_frame, text="Camera:", text_color="#888").pack(side="left")
        
        self.cam_var = ctk.StringVar(value="Select Camera")
        self.cam_dropdown = ctk.CTkComboBox(
            cam_frame,
            variable=self.cam_var,
            width=200,
            command=self.on_camera_change
        )
        self.cam_dropdown.pack(side="left", padx=10, fill="x", expand=True)
        
        # Preview Container (Fixed Size)
        self.preview_container = ctk.CTkFrame(self.frame, fg_color="#0f0f1a", corner_radius=8, height=220)
        self.preview_container.pack(fill="x", padx=10, pady=10)
        self.preview_container.pack_propagate(False)  # Prevent resizing
        
        self.preview_label = ctk.CTkLabel(self.preview_container, text="No Signal", text_color="#333")
        self.preview_label.pack(expand=True, fill="both")
        
        # Recognition Status
        self.rec_label = ctk.CTkLabel(
            self.frame, text="👁️ Scanning...", text_color="#666", font=ctk.CTkFont(size=12)
        )
        self.rec_label.pack(anchor="w", padx=15)
        
        # Prompt
        ctk.CTkLabel(self.frame, text="Prompt:", text_color="#888").pack(anchor="w", padx=10)
        self.prompt_entry = ctk.CTkEntry(
            self.frame,
            placeholder_text=f"Prompt for {title}...",
            fg_color="#0f0f1a",
            border_color="#3d3d5c"
        )
        self.prompt_entry.pack(fill="x", padx=10, pady=5)
        # Default prompt
        self.default_prompt = "Steel katana sword cartoon style"
        self.prompt_entry.insert(0, self.default_prompt)
        
        # --- Output Section ---
        ctk.CTkLabel(
            self.frame,
            text=f"🎨 AI Output",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color
        ).pack(pady=(15, 5))
        
        # Output Container (Fixed Size)
        self.output_container = ctk.CTkFrame(self.frame, fg_color="#0f0f1a", corner_radius=8)
        self.output_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.output_container.pack_propagate(False)

        self.output_label = ctk.CTkLabel(self.output_container, text="Waiting...", text_color="#333")
        self.output_label.pack(expand=True, fill="both")

    def update_cameras(self, cameras):
        """Update camera dropdown options."""
        if cameras:
            # list of (index, name)
            options = [f"{idx}: {name}" for idx, name in cameras]
            self.cam_dropdown.configure(values=options)
            
            # Restore selection if exists
            if self.cap_index is not None:
                for opt in options:
                    if opt.startswith(f"{self.cap_index}:"):
                        self.cam_var.set(opt)
                        break
        else:
            self.cam_dropdown.configure(values=["No cameras"])
    
    def on_camera_change(self, value):
        """Handle camera selection."""
        try:
            # Value format "idx: name"
            idx = int(value.split(':')[0])
            
            if self.camera:
                self.camera.close()
            
            self.camera = Camera(idx)
            if self.camera.open():
                self.cap_index = idx
                self.app.log(f"Camera {idx} assigned", "camera", self.role)
            else:
                self.app.log(f"Failed to open Camera {idx}", "error", self.role)
                self.camera = None
        except Exception as e:
            print(f"Cam select error: {e}")

    def update_preview(self):
        """Update live preview."""
        if self.camera:
            frame = self.camera.get_frame_for_display()
            if frame is not None:
                img = Image.fromarray(frame)
                
                # Use container size
                w = self.preview_container.winfo_width()
                h = self.preview_container.winfo_height()
                
                if w > 10 and h > 10:
                    # Maintain Aspect Ratio
                    img_ratio = img.width / img.height
                    target_ratio = w / h
                    
                    if img_ratio > target_ratio:
                        new_w = w
                        new_h = int(w / img_ratio)
                    else:
                        new_h = h
                        new_w = int(h * img_ratio)
                        
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
                    
                    self.preview_label.configure(image=photo, text="")
                    self.preview_label._image = photo

    def update_output(self, image_bytes):
        """Update AI output image."""
        try:
            img = Image.open(BytesIO(image_bytes))
            
            w = self.output_container.winfo_width()
            h = self.output_container.winfo_height()
            
            if w > 10 and h > 10:
                # Maintain Aspect Ratio
                img_ratio = img.width / img.height
                target_ratio = w / h
                
                if img_ratio > target_ratio:
                    new_w = w
                    new_h = int(w / img_ratio)
                else:
                    new_h = h
                    new_w = int(h * img_ratio)
                
                img = img.resize((new_w, new_h), Image.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
                self.output_label.configure(image=photo, text="")
                self.output_label._image = photo
        except Exception as e:
            self.app.log(f"Display error: {e}", "error", self.role)
            
    def open_train_dialog(self):
        """Open dialog to train current view."""
        if not self.camera:
            return
            
        dialog = ctk.CTkInputDialog(text="Enter label (e.g. cloud, empty):", title="Train Object")
        label = dialog.get_input()
        if label:
            frame_bytes = self.camera.capture()
            if frame_bytes:
                threading.Thread(target=self.app.train_knn, args=(frame_bytes, label, self.role)).start()

class BattleCameraApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("⚔️ Battle Camera")
        self.geometry("1400x800")
        self.configure(fg_color="#0a0a14")
        
        # State
        self.ws = RiftWebSocket()
        self.knn = KNNService()
        self.running = False
        self.logs = []
        self.available_cameras = []
        
        # Dynamic Prompts Map
        self.prompts_map = {
            "cloud": "A fluffy white cloud in cartoon style, blue sky background",
            "sword": "Steel katana sword cartoon style",
            "empty": "Empty background"
        }
        
        # Panels
        self.panels = {}
        
        # Build UI
        self.build_ui()
        
        # Detect cameras
        self.detect_cameras()
        
        # Connect WebSocket
        self.connect_ws()
        
        # Start loops
        self.update_previews_loop()
    
    def log(self, message: str, level: str = "info", role: str = ""):
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icons = {
            "info": "ℹ️", "success": "✅", "error": "❌",
            "camera": "📷", "ai": "🎨", "bg": "✂️", 
            "ws": "📡", "timer": "⏱️", "knn": "👁️"
        }
        icon = icons.get(level, "•")
        
        role_tag = f"[{role.upper()}] " if role else ""
        log_line = f"[{timestamp}] {role_tag}{icon} {message}"
        
        self.logs.append(log_line)
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        self.update_log_display()
    
    def update_log_display(self):
        """Update logs widget."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", "\n".join(self.logs))
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def build_ui(self):
        """Build main UI."""
        # Top Panel
        top = ctk.CTkFrame(self, height=50, fg_color="#1a1a2e")
        top.pack(fill="x")
        top.pack_propagate(False)
        
        ctk.CTkLabel(top, text="⚔️ BATTLE CAMERA", font=ctk.CTkFont(size=20, weight="bold"), text_color="#a855f7").pack(side="left", padx=20)
        
        self.ws_label = ctk.CTkLabel(top, text="● Connecting...", text_color="#fbbf24")
        self.ws_label.pack(side="left", padx=20)

        # Main Area
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 1. Nightmare Panel
        self.panels['nightmare'] = Panel(
            main, "nightmare", "🌙 NIGHTMARE", "#ec4899", self
        )
        
        # 2. Dream Panel
        self.panels['dream'] = Panel(
            main, "dream", "☀️ DREAM", "#3b82f6", self
        )
        
        # 3. Logs Panel (Right)
        log_frame = ctk.CTkFrame(main, width=300, fg_color="#1a1a2e")
        log_frame.pack(side="left", fill="y", padx=5, pady=5)
        log_frame.pack_propagate(False)
        
        ctk.CTkLabel(log_frame, text="📋 Logs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Monaco", size=11),
            fg_color="#0f0f1a",
            text_color="#aaa",
            activate_scrollbars=False
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_text.configure(state="disabled")
        
        # Bottom Controls
        controls = ctk.CTkFrame(self, height=70, fg_color="#1a1a2e")
        controls.pack(fill="x", pady=(0,0))
        
        self.start_btn = ctk.CTkButton(
            controls, text="▶ START ALL", 
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#22c55e", hover_color="#16a34a",
            width=200, height=50, 
            command=self.start
        )
        self.start_btn.pack(side="left", padx=20, pady=10)
        
        self.stop_btn = ctk.CTkButton(
            controls, text="⏹ STOP",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#ef4444", hover_color="#dc2626",
            width=200, height=50,
            state="disabled",
            command=self.stop
        )
        self.stop_btn.pack(side="left", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(controls, text="Ready", text_color="#888")
        self.status_label.pack(side="right", padx=20)

    def detect_cameras(self):
        """Detect and populate cameras."""
        self.log("Scanning cameras...", "camera")
        # tuple (index, name)
        self.available_cameras = list_cameras()
        
        for panel in self.panels.values():
            panel.update_cameras(self.available_cameras)
            
        self.log(f"Found {len(self.available_cameras)} cameras", "success")

    def connect_ws(self):
        def on_connect():
            self.after(0, lambda: self.ws_label.configure(text="● Connected", text_color="#22c55e"))
            self.log("WebSocket connected", "ws")
        def on_disconnect():
            self.after(0, lambda: self.ws_label.configure(text="● Disconnected", text_color="#ef4444"))
            self.log("WebSocket disconnected", "ws")
        self.ws.connect(on_connect, on_disconnect)

    def update_previews_loop(self):
        """Loop to update camera previews."""
        for panel in self.panels.values():
            panel.update_preview()
        self.after(33, self.update_previews_loop)
    
    def train_knn(self, image_bytes, label, role):
        """Train KNN with new sample."""
        try:
            self.log(f"Training '{label}'...", "knn", role)
            if self.knn.add_sample(image_bytes, label):
                self.log(f"Learned '{label}'", "success", role)
            else:
                self.log("Training failed", "error", role)
        except Exception as e:
            self.log(f"Train error: {e}", "error", role)

    def start(self):
        """Start all."""
        # Check if cameras are selected
        active_panels = [p for p in self.panels.values() if p.camera is not None]
        if not active_panels:
            self.log("No cameras selected!", "error")
            return
            
        if not get_api_key():
            self.log("FAL_KEY missing", "error")
            return
            
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log("Starting loop...", "success")
        
        self.transform_loop()

    def stop(self):
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.log("Stopped", "info")

    def transform_loop(self):
        if not self.running:
            return
        
        # Fire threads for each active panel
        for role, panel in self.panels.items():
            if panel.camera:
                threading.Thread(target=self.process_role, args=(role, panel), daemon=True).start()
        
        self.after(5000, self.transform_loop)

    def process_role(self, role, panel):
        """Process logic for one role."""
        try:
            start = time.time()
            frame_bytes = panel.camera.capture()
            if not frame_bytes: return
            
            # 1. KNN Recognition
            label, dist = self.knn.predict(frame_bytes)
            is_recognised = False
            
            # Confidence Threshold (approx)
            if label != "Need Training" and label != "Error" and dist < 22.0:
                is_recognised = (label != "empty") # "empty" is a valid label but means "no object"
                
                # Update UI Status
                conf = f"Dist: {dist:.1f}"
                self.after(0, lambda: panel.rec_label.configure(
                    text=f"👁️ {label.upper()} ({conf})", 
                    text_color="#22c55e" if is_recognised else "#888"
                ))
                
                # Update Prompt if recognized
                if is_recognised:
                    new_prompt = self.prompts_map.get(label, f"{label} in cartoon style")
                    current = panel.prompt_entry.get()
                    # Only update if different to allow manual override
                    if current != new_prompt:
                        self.after(0, lambda: panel.prompt_entry.delete(0, "end"))
                        self.after(10, lambda: panel.prompt_entry.insert(0, new_prompt))
                        self.log(f"Prompt set to '{label}'", "knn", role)
            else:
                 self.after(0, lambda: panel.rec_label.configure(text=f"👁️ ?", text_color="#666"))

            # 2. AI Transform
            prompt = panel.prompt_entry.get() 
            # If prompt is explicitly "Empty background", maybe skip AI? 
            # For now we generate anyway.
            
            self.log("AI Transform...", "ai", role)
            result, t_time = transform_image(frame_bytes, prompt)
            
            # 3. BG Removal
            final, bg_time = remove_background(result)
            self.after(0, lambda: panel.update_output(final))
            
            # 4. WebSocket
            b64 = base64.b64encode(final).decode('utf-8')
            payload_extra = {
                f"battle_drawing_{role}_recognised": is_recognised
            }
            
            if self.ws.send_image(b64, role, extra_data=payload_extra):
                self.log("Sent ✓", "success", role)
            
        except Exception as e:
            self.log(f"Error: {str(e)[:40]}", "error", role)

    def cleanup(self):
        self.running = False
        for panel in self.panels.values():
            if panel.camera:
                panel.camera.close()
        self.ws.close()


def main():
    app = BattleCameraApp()
    app.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), app.destroy()))
    app.mainloop()


if __name__ == "__main__":
    main()
