class CoordinatorButtonDelegate:
    def __init__(self, workshop, button_index):
        self.workshop = workshop
        self.button_index = button_index

    def on_press(self):
        if self.workshop:
            self.workshop.on_button_event(self.button_index)

    def on_release(self):
        pass
