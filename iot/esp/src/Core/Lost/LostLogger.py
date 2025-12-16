"""
LostLogger.py - Encapsulates logging logic for LOST workshop
"""
import src.Core.Lost.LostConstants as LC

class LostLogger:
    def __init__(self, logger):
        self.logger = logger

    def log_transition(self, from_step, to_step):
        """Log step transition with visual separator"""
        self.logger.info("-------- {} -> {} --------".format(
            LC.STEP_NAMES.get(from_step, str(from_step)),
            LC.STEP_NAMES.get(to_step, str(to_step))
        ))

    def log_ws(self, msg):
        """Log WebSocket message with separators"""
        self.logger.debug("-------------------------------")
        self.logger.debug("WS SEND: {}".format(msg))
        self.logger.debug("-------------------------------")

    def log_event(self, room, deco, module, action):
        """Log telemetry event in readable format"""
        rooms = {"parent": "Parent", "child": "Enfant", "system": "System"}
        self.logger.debug("Room: {} | Deco: {} | Module: {} | Action: {}".format(
            rooms.get(room, room), deco, module, action
        ))
