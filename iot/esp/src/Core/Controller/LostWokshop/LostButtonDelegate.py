import uasyncio as asyncio
from src.Framework.Button.ButtonDelegate import ButtonDelegate

class LostButtonDelegate(ButtonDelegate):
    def __init__(self, controller):
        self.controller = controller

    def on_click(self):
        try:
            asyncio.create_task(self.controller.handle_short_press())
        except Exception as e:
            print("Error in LostButtonDelegate:", e)