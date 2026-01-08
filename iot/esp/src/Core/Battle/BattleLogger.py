"""
BattleLogger.py - Logging helper for BATTLE workshop
"""

class BattleLogger:
    def __init__(self, controller_logger):
        self.logger = controller_logger

    def info(self, msg):
        self.logger.info(f"[BATTLE] {msg}")

    def error(self, msg):
        self.logger.error(f"[BATTLE] {msg}")

    def log_transition(self, from_step, to_step):
        import src.Core.Battle.BattleConstants as BC
        from_name = BC.BattleSteps.get_name(from_step)
        to_name = BC.BattleSteps.get_name(to_step)
        self.logger.info(f"[BATTLE] TRANSITION: {from_name} -> {to_name}")

    def log_ws(self, msg):
        self.logger.info(f"[BATTLE][WS] {msg}")
