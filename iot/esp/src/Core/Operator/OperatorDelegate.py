try:
    from src.Framework.Button.ButtonDelegate import ButtonDelegate
    from src.Framework.Rfid.RfidDelegate import RfidDelegate
except ImportError:
    pass

class OperatorButtonDelegate(ButtonDelegate):
    def __init__(self, workshop, button_type):
        self.workshop = workshop
        self.button_type = button_type # "rift" or "battle"

    def on_click(self):
        if self.workshop:
            self.workshop.on_button_press(self.button_type)

class OperatorRfidDelegate(RfidDelegate):
    def __init__(self, workshop):
        self.workshop = workshop

    def on_read(self, uid):
        if self.workshop:
            self.workshop.on_rfid_read(uid)
