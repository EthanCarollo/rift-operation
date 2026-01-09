"""Reusable GUI components."""
import customtkinter as ctk
from PIL import Image
from io import BytesIO
from datetime import datetime

class CameraPreview(ctk.CTkFrame):
    """Fixed aspect-ratio camera preview."""
    def __init__(self, parent, height=220, text="No Signal", **kwargs):
        super().__init__(parent, height=height, **kwargs)
        self.pack_propagate(False)
        self.configure(fg_color="#0f0f1a", corner_radius=8)
        
        self.label = ctk.CTkLabel(self, text=text, text_color="#333")
        self.label.pack(expand=True, fill="both")
        
    def update_image(self, image_bytes):
        """Update displayed image from bytes."""
        try:
            img = Image.open(BytesIO(image_bytes))
            self._display_pil(img)
        except Exception:
            pass
            
    def _display_pil(self, img):
        """Internal display helper."""
        w = self.winfo_width()
        h = self.winfo_height()
        
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
            self.label.configure(image=photo, text="")
            self.label._image = photo

class LogPanel(ctk.CTkFrame):
    """Scrollable log panel."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        ctk.CTkLabel(self, text="📋 Logs", font=ctk.CTkFont(size=14, weight="bold"), text_color="#888").pack(pady=5, anchor="w", padx=10)
        
        self.text_widget = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Monaco", size=11),
            fg_color="#0f0f1a",
            text_color="#aaa",
            activate_scrollbars=False
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_widget.configure(state="disabled")
        self.logs = []
        
    def log(self, message, level="info", role=""):
        """Add log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "info": "ℹ️", "success": "✅", "error": "❌",
            "camera": "📷", "ai": "🎨", "bg": "✂️", 
            "ws": "📡", "timer": "⏱️", "knn": "👁️"
        }
        icon = icons.get(level, "•")
        role_tag = f"[{role.upper()}] " if role else ""
        
        line = f"[{timestamp}] {role_tag}{icon} {message}"
        self.logs.append(line)
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
            
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", "\n".join(self.logs))
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
