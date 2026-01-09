#!/usr/bin/env python3
"""
Battle Camera - Main Entry Point.
Manages views (Battle vs Training) and shared services.
"""
import customtkinter as ctk
from dotenv import load_dotenv

# Import shared services
from src import KNNService, RiftWebSocket
# Import Views
from src.gui import BattleView, TrainingView
# Import Web Server
from src.web_server import start_server, set_battle_view, stop_server

load_dotenv()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚔️ Battle Camera System")
        self.geometry("1400x800")
        self.configure(fg_color="#0a0a14")
        
        # Shared Services
        self.knn = KNNService(dataset_name="default_dataset")
        self.ws = RiftWebSocket()
        self.ws.connect()
        
        # View Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        self.current_view = None
        self.show_battle()
        
    def show_battle(self):
        """Switch to Battle View."""
        if self.current_view:
            try:
                self.current_view.cleanup()
            except: pass
            self.current_view.destroy()
            
        self.current_view = BattleView(
            self.container, 
            ws=self.ws, 
            knn=self.knn, 
            open_training_callback=self.show_training
        )
        self.current_view.pack(fill="both", expand=True)
        
        # Start web server for remote monitoring
        set_battle_view(self.current_view)
        start_server(host='0.0.0.0', port=5000)
        
    def show_training(self):
        """Switch to Training View."""
        if self.current_view:
            try:
                self.current_view.cleanup()
            except: pass
            self.current_view.destroy()
            
        self.current_view = TrainingView(
            self.container, 
            knn_service=self.knn, 
            on_close=self.show_battle
        )
        self.current_view.pack(fill="both", expand=True)

    def on_close(self):
        """Cleanup on exit."""
        stop_server()
        if self.current_view:
            try:
                self.current_view.cleanup()
            except: pass
        self.ws.close()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
