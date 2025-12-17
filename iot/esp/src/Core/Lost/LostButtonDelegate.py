import uasyncio as asyncio
from src.Framework.Button.ButtonDelegate import ButtonDelegate

class LostButtonDelegate(ButtonDelegate):
    """
    Button delegate for the Lost workshop
    """
    def __init__(self, workshop):
        self.workshop = workshop

    def on_click(self):
        try:
            if self.workshop:
                asyncio.create_task(self.workshop.handle_short_press())
        except Exception as e:
            print("Error in LostButtonDelegate:", e)