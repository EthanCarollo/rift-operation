"""
LostLogger.py - Encapsulates logging logic for LOST workshop
"""
import src.Core.Lost.LostConstants as LC

class LostLogger:
    def __init__(self, logger):
        self.logger = logger

    def log_transition(self, from_step, to_step):
        """Log step transition with visual separator"""
        # Format: -------- 0: IDLE -> 1: DISTANCE --------
        self.logger.info(f"-------- {LC.LostSteps.get_name(from_step)} -> {LC.LostSteps.get_name(to_step)} --------")

    def log_ws(self, msg):
        """Log WebSocket message with separators"""
        self.logger.debug("-------------------------------")
        self.logger.debug(f"WS SEND: {msg}")
        self.logger.debug("-------------------------------")

    def log_event(self, room, deco, module, action):
        """Log telemetry event in readable format"""
        rooms = {"nightmare": "Nightmare", "dream": "Dream", "system": "System"}
        self.logger.debug(f"Room: {rooms.get(room, room)} | Deco: {deco} | Module: {module} | Action: {action}")

    # Passthrough methods to avoid .logger.logger access
    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
