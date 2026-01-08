"""
BattleButtonDelegate.py - Button delegate for Battle workshop
"""
import uasyncio as asyncio

class BattleButtonDelegate:
    def __init__(self, workshop):
        self.workshop = workshop

    def on_short_press(self):
        if self.workshop:
            asyncio.create_task(self.workshop.handle_short_press())

    def on_long_press(self):
        """Long press not used in Battle"""
        pass
