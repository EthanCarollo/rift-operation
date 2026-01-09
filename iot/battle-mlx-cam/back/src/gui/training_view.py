"""Training View for KNN."""
import customtkinter as ctk
import threading
import time
from datetime import datetime
from src import Camera, list_cameras, KNNService
from .components import CameraPreview

class TrainingView(ctk.CTkFrame):
    """Dedicated KNN Training Interface."""
    
    def __init__(self, parent, knn_service: KNNService, on_close=None):
        super().__init__(parent, fg_color="#0a0a14")
        self.knn = knn_service
        self.on_close = on_close
        self.camera = None
        self.is_capturing = False
        
        # UI Layout
        self._build_sidebar()
        self._build_main_area()
        
        # Initial State
        self._refresh_datasets()
        self._refresh_cameras()
        self._update_counts()

    def _build_sidebar(self):
        """Right sidebar for controls."""
        sidebar = ctk.CTkFrame(self, width=300, fg_color="#1a1a2e", corner_radius=0)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)
        
        ctk.CTkLabel(sidebar, text="🎓 TRAINING MODE", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # 1. Dataset Selection
        ctk.CTkLabel(sidebar, text="Dataset:", text_color="#888").pack(anchor="w", padx=20)
        self.ds_var = ctk.StringVar(value=self.knn.dataset_name)
        self.ds_menu = ctk.CTkComboBox(sidebar, variable=self.ds_var, command=self._on_dataset_change)
        self.ds_menu.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(sidebar, text="New Dataset", height=24, fg_color="#333", command=self._create_dataset).pack(fill="x", padx=20, pady=5)
        
        # 2. Camera Selection
        ctk.CTkLabel(sidebar, text="Training Camera:", text_color="#888").pack(anchor="w", padx=20, pady=(20, 0))
        self.cam_var = ctk.StringVar(value="Select Camera")
        self.cam_menu = ctk.CTkComboBox(sidebar, variable=self.cam_var, command=self._on_camera_change)
        self.cam_menu.pack(fill="x", padx=20, pady=5)
        
        # 3. Labeling
        from src.config import PROMPT_MAPPING
        ctk.CTkLabel(sidebar, text="Current Label:", text_color="#888").pack(anchor="w", padx=20, pady=(20, 0))
        
        # Sort labels to put non-recognition/empty at the end or beginning
        labels = sorted(list(PROMPT_MAPPING.keys()))
        
        self.current_label_str = labels[0] if labels else "cloud" # Thread-safe variable
        self.label_var = ctk.StringVar(value=self.current_label_str)
        self.label_menu = ctk.CTkComboBox(
            sidebar, 
            variable=self.label_var, 
            values=labels,
            state="readonly",
            command=self._on_label_change
        )
        self.label_menu.pack(fill="x", padx=20, pady=5)
        
        # 4. Train Action (Toggle)
        self.train_btn = ctk.CTkButton(
            sidebar,
            text="START TRAINING",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._toggle_training
        )
        self.train_btn.pack(fill="x", padx=20, pady=20)
        
        # 5. Tools
        tools_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        tools_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(tools_frame, text="Delete Label", fg_color="#ef4444", hover_color="#dc2626", 
                     width=100, command=self._delete_label).pack(side="left", expand=True, padx=5)
                     
        ctk.CTkButton(tools_frame, text="Clear All", fg_color="#b91c1c", hover_color="#991b1b", 
                     width=80, command=self._clear_dataset).pack(side="right", expand=True, padx=5)

        # 6. Status/Counts
        ctk.CTkLabel(sidebar, text="Class Counts:", text_color="#888").pack(anchor="w", padx=20, pady=(20, 5))
        self.counts_text = ctk.CTkTextbox(sidebar, height=150, fg_color="#1e1e2e")
        self.counts_text.pack(fill="x", padx=20, pady=5)
        
        # Back Button
        ctk.CTkButton(sidebar, text="← Back to Battle", fg_color="transparent", border_width=1, border_color="#555", command=self._close).pack(side="bottom", pady=20)

    def _build_main_area(self):
        """Center preview area."""
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.preview = CameraPreview(center, height=500, text="Select a camera to start")
        # Override preview height constraint
        self.preview.configure(height=500)
        self.preview.pack(fill="both", expand=True)
        
        # Feedback label overlay
        self.feedback_label = ctk.CTkLabel(center, text="", font=ctk.CTkFont(size=24, weight="bold"), text_color="#22c55e")
        self.feedback_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Loading Indicator
        self.loading_label = ctk.CTkLabel(center, text="⏳ Loading...", font=ctk.CTkFont(size=16), text_color="#fbbf24")
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.loading_label.place_forget()
        
        self.allow_preview = False  # Control flag for preview loop

    def _set_loading(self, show: bool):
        if show:
            self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.loading_label.place_forget()

    def _close(self):
        self.allow_preview = False  # Stop loop
        if self.camera:
            self.camera.close()
            self.camera = None
        if self.on_close:
            self.on_close()
            
    def _refresh_datasets(self):
        threading.Thread(target=self._refresh_datasets_thread, daemon=True).start()

    def _refresh_datasets_thread(self):
        self.after(0, lambda: self._set_loading(True))
        datasets = self.knn.list_datasets()
        self.after(0, lambda: self.ds_menu.configure(values=datasets))
        self.after(0, lambda: self.ds_var.set(self.knn.dataset_name))
        self.after(0, lambda: self._set_loading(False))
        
    def _create_dataset(self):
        dialog = ctk.CTkInputDialog(text="New Dataset Name:", title="Create Dataset")
        text = dialog.get_input()
        if text:
            clean = "".join(c for c in text if c.isalnum() or c in ('_', '-'))
            self.knn.set_dataset(clean)
            self._refresh_datasets()
            self._update_counts()

    def _on_dataset_change(self, choice):
        threading.Thread(target=self._change_dataset_thread, args=(choice,), daemon=True).start()
        
    def _change_dataset_thread(self, choice):
        self.after(0, lambda: self._set_loading(True))
        self.knn.set_dataset(choice)
        self._update_counts()
        self.after(0, lambda: self._set_loading(False))

    def _refresh_cameras(self):
        threading.Thread(target=self._refresh_cameras_thread, daemon=True).start()
        
    def _refresh_cameras_thread(self):
        cams = list_cameras()
        if cams:
            options = [f"{idx}: {name}" for idx, name in cams]
            self.after(0, lambda: self.cam_menu.configure(values=options))
            self.after(0, lambda: self.cam_var.set("Select Camera"))
        else:
            self.after(0, lambda: self.cam_menu.configure(values=["No cameras"]))
            
    def _on_camera_change(self, choice):
        # Stop existing preview first
        self.allow_preview = False
        # Give UI time to update
        self.preview.label.configure(text="Switching...")
        threading.Thread(target=self._change_camera_thread, args=(choice,), daemon=True).start()
        
    def _change_camera_thread(self, choice):
        self.after(0, lambda: self._set_loading(True))
        
        # Wait a tiny bit for the loop to exit
        time.sleep(0.5) 
        
        try:
            parts = choice.split(':')
            if not parts or not parts[0].isdigit():
                return

            idx = int(parts[0])
            if self.camera:
                self.camera.close()
            
            new_cam = Camera(idx)
            if new_cam.open():
                self.camera = new_cam
                self.allow_preview = True
                print(f"[Training] Camera {idx} opened. Starting loop.")
                self.after(0, self._start_preview_loop)
            else:
                print(f"[Training] Failed to open camera {idx}")
                self.after(0, lambda: self.preview.label.configure(text=f"Failed to open Camera {idx}"))
                
        except Exception as e:
            print(f"Camera switch error: {e}")
            import traceback
            traceback.print_exc()
            self.after(0, lambda: self.preview.label.configure(text=f"Error: {e}"))
            
        self.after(0, lambda: self._set_loading(False))

    def _start_preview_loop(self):
        if not self.allow_preview:
            return

        if self.camera:
            try:
                frame_bytes = self.camera.capture()
                if frame_bytes:
                    self.preview.update_image(frame_bytes)
            except Exception as e:
                print(f"Preview error: {e}")

        if self.allow_preview:
            self.after(33, self._start_preview_loop)

    def _toggle_training(self):
        if self.is_capturing:
            self._stop_training()
        else:
            self._start_training()

    def _start_training(self):
        label = self.label_var.get()
        if not label: return
        
        self.is_capturing = True
        self.train_btn.configure(text="STOP TRAINING", fg_color="#ef4444", hover_color="#dc2626")
        threading.Thread(target=self._train_loop, daemon=True).start()

    def _stop_training(self):
        self.is_capturing = False
        self.train_btn.configure(text="START TRAINING", fg_color="#8b5cf6", hover_color="#7c3aed")
        self.knn.save()
        print("[Training] Saved samples to disk.")

    def _on_label_change(self, choice):
        self.current_label_str = choice
        # Also update if capturing? Yes, immediate switch.

    def _train_loop(self):
        while self.is_capturing:
            if not self.camera:
                break
            
            # Read label safely
            label = self.current_label_str
            
            frame = self.camera.capture()
            if frame:
                # Add sample without saving to disk every time (faster)
                if self.knn.add_sample(frame, label, save=False):
                    count = self.knn.get_counts().get(label, 0)
                    self.after(0, lambda l=label, c=count: self._update_overlay(l, c))
                    self.after(0, self._update_counts)
            
            # Rate limit training speed
            time.sleep(0.1)
            
        self.after(0, lambda: self._update_overlay(None, 0))
        
    def _delete_label(self):
        label = self.label_var.get()
        if label:
            self.knn.delete_label(label)
            self._update_counts()
            
    def _clear_dataset(self):
        name = self.knn.dataset_name
        self.knn.training_samples = []
        self.knn.save()
        self._update_counts()

    def _update_overlay(self, label, count):
        if label and count:
            text = f"Adding '{label}'... ({count})"
        else:
            text = "" # Clear feedback
        self.after(0, lambda: self.feedback_label.configure(text=text))

    def _update_counts(self):
        counts = self.knn.get_counts()
        txt = ""
        for k, v in counts.items():
            txt += f"{k}: {v}\n"
        
        self.after(0, lambda: self._set_stats(txt))
        
    def _set_stats(self, text):
        self.counts_text.configure(state="normal")
        self.counts_text.delete("1.0", "end")
        self.counts_text.insert("end", text)
        self.counts_text.configure(state="disabled")
