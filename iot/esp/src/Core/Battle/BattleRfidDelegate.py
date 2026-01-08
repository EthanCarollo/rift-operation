"""
BattleRfidDelegate.py - RFID delegate for Battle workshop
"""

class BattleRfidDelegate:
    def __init__(self, workshop):
        self.workshop = workshop

    def on_uid_read(self, uid, name):
        if self.workshop:
            self.workshop.on_rfid_read(uid)
