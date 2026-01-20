from src.Framework.Button.ButtonDelegate import ButtonDelegate

class OperatorButtonDelegate(ButtonDelegate):
    """Delegate for the main rift closure button"""
    def __init__(self, workshop):
        self.workshop = workshop

    def on_click(self):
        if self.workshop:
            self.workshop.on_button_press()
